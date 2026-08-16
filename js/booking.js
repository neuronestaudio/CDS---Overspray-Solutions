/* CDS booking wizard — pill-driven, auto-advancing.
   Flow: 1 service+how · 2 budget · 3 location (address if mobile / postcode if
   studio) · 4 vehicle + condition (label flips to "Paint condition" for
   paint jobs) · 5 details. First-touch attribution -> GTM generate_lead -> GHL.
   ---------------------------------------------------------------------------
   SET AFTER THE MEETING:
   - GTM: replace GTM-XXXXXXX in index.html <head> with the real container ID.
   - GHL: paste the GoHighLevel inbound webhook URL into CONFIG.GHL_ENDPOINT.
   --------------------------------------------------------------------------- */
(function () {
  "use strict";
  var CONFIG = { GHL_ENDPOINT: "" };

  var form = document.getElementById("bookingForm");
  if (!form) return;

  var steps   = Array.prototype.slice.call(form.querySelectorAll(".wiz-step"));
  var dots    = Array.prototype.slice.call(form.querySelectorAll("[data-step-dot]"));
  var backBtn = form.querySelector("[data-wiz-back]");
  var nextBtn = form.querySelector("[data-wiz-next]");
  var subBtn  = form.querySelector("[data-wiz-submit]");
  var okEl    = document.getElementById("bookOk");
  var cur = 0, advancing = false;

  var ATTR = firstTouch();

  function checked(name) { return form.querySelector('input[name="' + name + '"]:checked'); }
  function isMobile() { var f = checked("format"); return !!f && /mobile/i.test(f.value); }

  // address (mobile only) + condition label depend on earlier answers
  function syncConditional() {
    var mf = form.querySelector('.field[data-loc="mobile"]');
    if (mf) {
      var mob = isMobile();
      mf.hidden = !mob;
      var mi = mf.querySelector("input");
      if (mi) mi.required = mob;
    }
    var lbl = form.querySelector("[data-cond-label]");
    if (lbl) {
      var s = checked("service");
      lbl.textContent = (s && s.getAttribute("data-paint") === "1") ? "Paint condition" : "Overall condition";
    }
  }

  function show(i) {
    cur = i;
    steps.forEach(function (s, j) { s.hidden = j !== i; });
    dots.forEach(function (d, j) { d.classList.toggle("on", j <= i); });
    backBtn.hidden = i === 0;
    var last = i === steps.length - 1;
    nextBtn.hidden = last;
    subBtn.hidden = !last;
    var cnt = form.querySelector("[data-wiz-count]");
    if (cnt) cnt.textContent = "Step " + (i + 1) + " of " + steps.length;
    syncConditional();
    var f = steps[i].querySelector('.field:not([hidden]) input:not([type="radio"]), .field:not([hidden]) select, .field:not([hidden]) textarea');
    if (f) { try { f.focus({ preventScroll: true }); } catch (e) {} }
  }

  function validStep(i) {
    var s = steps[i], ok = true;
    s.querySelectorAll("[required]").forEach(function (el) {
      var host = el.closest(".field");
      if (host && host.hidden) return;                 // skip conditional-hidden fields
      var good;
      if (el.type === "radio") good = !!s.querySelector('input[name="' + el.name + '"]:checked');
      else good = !!el.value.trim();
      var h = host || el.closest(".wiz-choices");
      if (h) h.classList.toggle("invalid", !good);
      if (!good) ok = false;
    });
    return ok;
  }

  function goNext() { if (validStep(cur)) show(Math.min(cur + 1, steps.length - 1)); }
  nextBtn.addEventListener("click", goNext);
  backBtn.addEventListener("click", function () { show(Math.max(cur - 1, 0)); });

  // choice-only steps auto-advance; mobile waits for the address so it doesn't skip it
  function maybeAutoNext() {
    if (advancing || cur >= steps.length - 1) return;
    var ready = false;
    if (cur === 0) ready = !!checked("service");                                   // service
    else if (cur === 1) { var f = checked("format"); ready = !!f && !/mobile/i.test(f.value); } // studio only
    else if (cur === 2) ready = !!checked("budget");                               // budget
    if (!ready) return;
    advancing = true;
    setTimeout(function () { advancing = false; if (validStep(cur)) show(cur + 1); }, 340);
  }

  form.addEventListener("change", function (e) {
    var el = e.target;
    if (el && el.type === "radio") {
      form.querySelectorAll('input[name="' + el.name + '"]').forEach(function (r) {
        var label = r.closest(".wiz-pill, .wiz-choice, .wiz-tile");
        if (label) label.classList.toggle("checked", r.checked);
      });
      syncConditional();
      maybeAutoNext();
    }
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!validStep(cur)) return;

    var data = {};
    new FormData(form).forEach(function (v, k) { data[k] = v; });
    for (var k in ATTR) data[k] = ATTR[k];

    window.dataLayer = window.dataLayer || [];
    var evt = { event: "generate_lead", lead_source: "website_booking", form_name: "booking", currency: "AUD" };
    for (var d in data) evt[d] = data[d];
    window.dataLayer.push(evt);

    if (CONFIG.GHL_ENDPOINT) {
      try {
        fetch(CONFIG.GHL_ENDPOINT, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data), mode: "no-cors", keepalive: true
        });
      } catch (err) {}
    }

    form.querySelectorAll(".wiz-step,.wiz-nav,.wiz-progress,.form-note").forEach(function (el) { el.style.display = "none"; });
    if (okEl) okEl.classList.add("show");
  });

  function firstTouch() {
    var KEY = "cds_first_touch";
    try { var saved = JSON.parse(localStorage.getItem(KEY) || "null"); if (saved) return saved; } catch (e) {}
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
