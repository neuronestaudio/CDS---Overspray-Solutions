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

const str = (v) => (v === undefined || v === null ? '' : String(v)).trim();

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
      .map((k) => ({ key: k, field_value: str(body[k]).slice(0, 2000) }));

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

  // Always log the lead so it exists in the deployment logs even if GHL is down.
  console.log('LEAD', JSON.stringify({
    saved, contactId, email, phone,
    name: str(body.full_name) || str(body.name),
    service: str(body.service), budget: str(body.budget), vehicle: str(body.vehicle)
  }));

  return res.status(200).json({ ok: true, saved, id: contactId });
};
