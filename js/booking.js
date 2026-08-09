/* CDS booking wizard.
   Multi-step form -> first-touch attribution -> GTM `generate_lead` -> GHL.
   ---------------------------------------------------------------------------
   SET AFTER THE MEETING:
   - GTM: replace GTM-XXXXXXX in index.html <head> with the real container ID.
   - GHL: paste the GoHighLevel inbound webhook URL into CONFIG.GHL_ENDPOINT
     below. Leave blank to skip the network post (the form still fires
     generate_lead into the dataLayer and shows the success state).
   --------------------------------------------------------------------------- */
(function () {
  "use strict";
  var CONFIG = {
    GHL_ENDPOINT: "" // e.g. "https://services.leadconnectorhq.com/hooks/xxxx/webhook-trigger/xxxx"
  };

  var form = document.getElementById("bookingForm");
  if (!form) return;

  var steps   = Array.prototype.slice.call(form.querySelectorAll(".wiz-step"));
  var dots    = Array.prototype.slice.call(form.querySelectorAll("[data-step-dot]"));
  var backBtn = form.querySelector("[data-wiz-back]");
  var nextBtn = form.querySelector("[data-wiz-next]");
  var subBtn  = form.querySelector("[data-wiz-submit]");
  var okEl    = document.getElementById("bookOk");
  var cur = 0;

  var ATTR = firstTouch();

  function show(i) {
    cur = i;
    steps.forEach(function (s, j) { s.hidden = j !== i; });
    dots.forEach(function (d, j) { d.classList.toggle("on", j <= i); });
    backBtn.hidden = i === 0;
    var last = i === steps.length - 1;
    nextBtn.hidden = last;
    subBtn.hidden = !last;
    var first = steps[i].querySelector("input,select,textarea");
    if (first) { try { first.focus({ preventScroll: true }); } catch (e) { first.focus(); } }
  }

  function validStep(i) {
    var s = steps[i], ok = true;
    s.querySelectorAll("[required]").forEach(function (el) {
      var good;
      if (el.type === "radio") good = !!s.querySelector('input[name="' + el.name + '"]:checked');
      else good = !!el.value.trim();
      var host = el.closest(".field") || el.closest(".wiz-choices");
      if (host) host.classList.toggle("invalid", !good);
      if (!good) ok = false;
    });
    return ok;
  }

  nextBtn.addEventListener("click", function () { if (validStep(cur)) show(Math.min(cur + 1, steps.length - 1)); });
  backBtn.addEventListener("click", function () { show(Math.max(cur - 1, 0)); });

  // highlight selected format choice (no :has() dependency)
  form.querySelectorAll('input[name="format"]').forEach(function (r) {
    r.addEventListener("change", function () {
      form.querySelectorAll(".wiz-choice").forEach(function (c) {
        c.classList.toggle("checked", c.contains(r) && r.checked);
      });
    });
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!validStep(cur)) return;

    var data = {};
    new FormData(form).forEach(function (v, k) { data[k] = v; });
    for (var k in ATTR) data[k] = ATTR[k];

    // 1) GTM dataLayer conversion event
    window.dataLayer = window.dataLayer || [];
    var evt = { event: "generate_lead", lead_source: "website_booking", form_name: "booking", currency: "AUD" };
    for (var d in data) evt[d] = data[d];
    window.dataLayer.push(evt);

    // 2) GoHighLevel
    if (CONFIG.GHL_ENDPOINT) {
      try {
        fetch(CONFIG.GHL_ENDPOINT, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
          mode: "no-cors",
          keepalive: true
        });
      } catch (err) { /* non-blocking */ }
    }

    form.querySelectorAll(".wiz-step,.wiz-nav,.wiz-progress,.form-note").forEach(function (el) { el.style.display = "none"; });
    if (okEl) okEl.classList.add("show");
  });

  function firstTouch() {
    var KEY = "cds_first_touch";
    try {
      var saved = JSON.parse(localStorage.getItem(KEY) || "null");
      if (saved) return saved;
    } catch (e) {}
    var q = new URLSearchParams(location.search);
    var g = function (k) { return q.get(k) || ""; };
    var a = {
      utm_source: g("utm_source"), utm_medium: g("utm_medium"), utm_campaign: g("utm_campaign"),
      utm_term: g("utm_term"), utm_content: g("utm_content"),
      gclid: g("gclid"), fbclid: g("fbclid"), gbraid: g("gbraid"), wbraid: g("wbraid"),
      referrer: document.referrer || "", landing_page: location.pathname + location.search,
      first_seen: new Date().toISOString()
    };
    try { localStorage.setItem(KEY, JSON.stringify(a)); } catch (e) {}
    return a;
  }

  show(0);
})();
