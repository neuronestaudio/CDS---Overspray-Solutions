/* Booking form -> GoHighLevel.
 *
 * The form used to POST straight to a GHL inbound-webhook trigger. That trigger
 * answers 200 even when its workflow is unpublished, so every lead was accepted
 * and thrown away (CDS had 0 contacts on 20 Sep 2026). This writes the contact
 * with the API instead, so the lead is saved whatever the workflow is doing, and
 * still pokes the webhook afterwards so automations fire once it is published.
 *
 * Env (Vercel project cds-overspray-solutions):
 *   GHL_TOKEN        private integration token (pit-...)
 *   GHL_LOCATION_ID  sub-account id
 *   GHL_WEBHOOK      inbound webhook URL, optional
 *   GHL_ALERT_CONTACT_ID  optional override for the lead-alert contact below
 *
 * EMAIL ALERT: the workflow texts Andy but has no email step, and workflow steps
 * cannot be edited over the API. So this sends the alert itself, through GHL's
 * conversations API. That API only mails an address that belongs to a contact,
 * hence the internal contact "Website Lead Alerts (internal)" whose email is
 * info@cardetailingsolutions.com.au (DND on SMS/calls, email left open). The
 * alerts thread under that contact in GHL's inbox.
 *
 * GOTCHA: custom fields only save when addressed by BARE key ("service") or by
 * field id. The "contact.service" form the API hands you in customFields listings
 * is accepted, returns 200, and silently stores nothing.
 */
const GHL = 'https://services.leadconnectorhq.com';

// bare keys, matching the sub-account's field keys minus the "contact." prefix
const FIELD_KEYS = [
  'service', 'service_option', 'service_interest', 'type_of_service', 'budget', 'condition',
  'vehicle', 'make', 'car_model', 'message', 'how_soon', 'format',
  'lead_source', 'form_name', 'submission_id', 'confirmation_number',
  'landing_page', 'first_landing_page', 'referrer', 'first_seen',
  'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
  'gclid', 'fbclid', 'gbraid', 'wbraid', 'msclkid'
];

// GHL reserves some names as native contact keys and refuses to create a custom
// field using one. "gclid" is the trap: the field cannot exist in the sub-account,
// so the value was accepted by the upsert and silently dropped (verified 27 Sep
// 2026 - 7 of 8 fields saved, gclid was the one missing). The field is named
// "Google Click ID" (key google_click_id) and the form's own name maps onto it here.
const KEY_ALIAS = { gclid: 'google_click_id' };

const ALERT_CONTACT_ID = process.env.GHL_ALERT_CONTACT_ID || '7ZBvk22e35iWd22XjxXQ';

const str = (v) => (v === undefined || v === null ? '' : String(v)).trim();

const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// Same facts as the SMS alert, laid out for a phone's mail app.
function alertEmail(body, { name, phone, email, contactId, locationId }) {
  const rows = [
    ['Name', name],
    ['Phone', phone && `<a href="tel:${esc(phone)}">${esc(phone)}</a>`, true],
    ['Email', email && `<a href="mailto:${esc(email)}">${esc(email)}</a>`, true],
    ['Service', str(body.service)],
    ['Vehicle', str(body.vehicle)],
    ['Condition', str(body.condition)],
    ['Budget', str(body.budget)],
    ['Message', str(body.message)],
    ['Source', [str(body.lead_source), str(body.utm_source)].filter(Boolean).join(' / ')],
    ['Page', str(body.landing_page)]
  ].filter(([, v]) => v);

  const table = rows.map(([k, v, raw]) =>
    `<tr><td style="padding:6px 14px 6px 0;color:#666;vertical-align:top;white-space:nowrap">${k}</td>` +
    `<td style="padding:6px 0;color:#111">${raw ? v : esc(v).replace(/\n/g, '<br>')}</td></tr>`).join('');

  const link = contactId
    ? `<p style="margin:20px 0 0"><a href="https://app.gohighlevel.com/v2/location/${locationId}/contacts/detail/${contactId}" ` +
      `style="background:#111;color:#fff;padding:10px 16px;border-radius:6px;text-decoration:none">Open in GHL</a></p>`
    : '';

  return {
    subject: `New website lead: ${name || phone || email}${str(body.service) ? ` - ${str(body.service)}` : ''}`,
    html: `<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.4">` +
      `<p style="margin:0 0 12px"><strong>New lead from cardetailingsolutions.com.au</strong></p>` +
      `<table style="border-collapse:collapse">${table}</table>${link}</div>`
  };
}

function splitName(body) {
  const full = str(body.full_name) || str(body.name);
  if (!full) return { firstName: '', lastName: '' };
  const bits = full.split(/\s+/);
  return bits.length === 1
    ? { firstName: bits[0], lastName: '' }
    : { firstName: bits.slice(0, -1).join(' '), lastName: bits[bits.length - 1] };
}

async function postJson(url, headers, payload, ms = 8000) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), ms);
  try {
    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...headers },
      body: JSON.stringify(payload),
      signal: ctrl.signal
    });
    const text = await r.text();
    return { ok: r.ok, status: r.status, text };
  } finally {
    clearTimeout(timer);
  }
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch { return res.status(400).json({ error: 'Bad JSON' }); }
  }
  if (!body || typeof body !== 'object') return res.status(400).json({ error: 'Bad request' });

  const email = str(body.email);
  const phone = str(body.phone) || str(body.mobile);
  if (!email && !phone) return res.status(400).json({ error: 'Need an email or a phone number' });

  const token = process.env.GHL_TOKEN;
  const locationId = process.env.GHL_LOCATION_ID;
  const webhook = process.env.GHL_WEBHOOK;

  let saved = false;
  let contactId = null;

  if (token && locationId) {
    const { firstName, lastName } = splitName(body);
    const customFields = FIELD_KEYS
      .filter((k) => str(body[k]))
      .map((k) => ({ key: KEY_ALIAS[k] || k, field_value: str(body[k]).slice(0, 2000) }));

    const payload = {
      locationId,
      firstName,
      lastName,
      source: str(body.lead_source) || 'website',
      tags: ['website lead'],
      customFields
    };
    if (email) payload.email = email;
    if (phone) payload.phone = phone;

    try {
      const r = await postJson(`${GHL}/contacts/upsert`, {
        Authorization: `Bearer ${token}`,
        Version: '2021-07-28',
        Accept: 'application/json'
      }, payload);
      if (r.ok) {
        saved = true;
        try { contactId = JSON.parse(r.text).contact.id; } catch { /* id is a nicety */ }
      } else {
        console.error('GHL upsert failed', r.status, r.text.slice(0, 500));
      }
    } catch (err) {
      console.error('GHL upsert threw', err && err.message);
    }
  } else {
    console.error('GHL_TOKEN or GHL_LOCATION_ID missing - lead not written to the CRM');
  }

  // Fire the workflow too. Harmless while it is a draft; once it is published
  // this is what sends the notification. Never let it fail the request.
  if (webhook) {
    try {
      const w = await postJson(webhook, {}, body, 5000);
      if (!w.ok) console.error('GHL webhook failed', w.status, w.text.slice(0, 300));
    } catch (err) {
      console.error('GHL webhook threw', err && err.message);
    }
  }

  // Email Andy. Never let it fail the request.
  let emailed = false;
  if (token && locationId && ALERT_CONTACT_ID) {
    try {
      const name = str(body.full_name) || str(body.name);
      const msg = alertEmail(body, { name, phone, email, contactId, locationId });
      const a = await postJson(`${GHL}/conversations/messages`, {
        Authorization: `Bearer ${token}`,
        Version: '2021-07-28',
        Accept: 'application/json'
      }, { type: 'Email', contactId: ALERT_CONTACT_ID, emailFrom: 'CDS Website <info@cardetailingsolutions.com.au>', ...msg }, 6000);
      emailed = a.ok;
      if (!a.ok) console.error('GHL alert email failed', a.status, a.text.slice(0, 300));
    } catch (err) {
      console.error('GHL alert email threw', err && err.message);
    }
  }

  // Always log the lead so it exists in the deployment logs even if GHL is down.
  console.log('LEAD', JSON.stringify({
    saved, emailed, contactId, email, phone,
    name: str(body.full_name) || str(body.name),
    service: str(body.service), budget: str(body.budget), vehicle: str(body.vehicle)
  }));

  return res.status(200).json({ ok: true, saved, id: contactId });
};
