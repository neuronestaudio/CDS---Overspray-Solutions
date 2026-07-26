/* =========================================================================
   CDS · Overspray Solutions - interactions
   No window scroll listeners. IntersectionObserver for nav + reveals.
   ========================================================================= */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var qaMode = /[?&]qa\b/.test(location.search); // reveals everything up-front for QA/screenshots

  /* ---------- Nav glass on scroll (sentinel, not scroll listener) ---------- */
  var nav = document.getElementById("nav");
  var sentinel = document.createElement("div");
  sentinel.style.cssText = "position:absolute;top:0;left:0;width:1px;height:60px;pointer-events:none";
  document.body.prepend(sentinel);
  new IntersectionObserver(function (entries) {
    nav.classList.toggle("scrolled", !entries[0].isIntersecting);
  }, { threshold: 0 }).observe(sentinel);

  /* ---------- Hero A/B compare (?hero=a | ?hero=b) ---------- */
  var heroParam = (location.search.match(/[?&]hero=([a-z0-9]+)/i) || [])[1];
  if (heroParam) {
    var heroSrc = { a: "assets/img/hero-a.png", b: "assets/img/hero-b.png", c: "assets/img/hero-c.png" };
    var hImg = document.querySelector(".hero-media img");
    if (hImg && heroSrc[heroParam]) {
      document.querySelector(".hero").classList.add("hero-" + heroParam);
      hImg.onerror = function () {
        hImg.style.display = "none"; // fall back to CSS gradient
        var note = document.createElement("div");
        note.className = "hero-missing";
        note.textContent = "Preview mode: save your image as assets/img/hero-" + heroParam + ".jpg to see it here";
        var host = document.querySelector(".hero .wrap");
        if (host) host.appendChild(note);
      };
      hImg.src = heroSrc[heroParam];
    }
  }

  /* ---------- Scroll reveals ---------- */
  var reveals = document.querySelectorAll(".reveal");
  if (reduceMotion || qaMode) {
    reveals.forEach(function (el) { el.classList.add("in"); });
  } else {
    var ro = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); obs.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
    reveals.forEach(function (el) { if (!el.classList.contains("in")) ro.observe(el); });
  }

  /* ---------- Mobile drawer ---------- */
  var burger = document.getElementById("burger");
  var drawer = document.getElementById("drawer");
  var drawerClose = document.getElementById("drawerClose");
  function openDrawer() { drawer.classList.add("open"); drawer.setAttribute("aria-hidden", "false"); burger.setAttribute("aria-expanded", "true"); document.body.style.overflow = "hidden"; }
  function closeDrawer() { drawer.classList.remove("open"); drawer.setAttribute("aria-hidden", "true"); burger.setAttribute("aria-expanded", "false"); document.body.style.overflow = ""; }
  burger.addEventListener("click", openDrawer);
  drawerClose.addEventListener("click", closeDrawer);
  drawer.querySelectorAll("a").forEach(function (a) { a.addEventListener("click", closeDrawer); });

  /* ---------- Work pool (floating carousel) ---------- */
  var cats = { coating: [15, 16, 24, 25, 31, 32], fleet: [26, 27, 28, 29, 30] };
  function catLabel(c) { return c === "coating" ? "Coating" : c === "fleet" ? "Fleet" : "Detailing"; }
  var items = [];
  for (var i = 1; i <= 32; i++) {
    var n = ("0" + i).slice(-2);
    var cat = "detail";
    if (cats.coating.indexOf(i) > -1) cat = "coating";
    else if (cats.fleet.indexOf(i) > -1) cat = "fleet";
    items.push({ n: n, cat: cat });
  }
  var srcs = items.map(function (it) { return "assets/gallery/" + it.n + ".jpg"; }); // lightbox order

  var ratios = ["4 / 3", "1 / 1", "3 / 4", "5 / 4", "4 / 3", "16 / 10"];
  var expandSvg = '<span class="pool-exp"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg></span>';

  function makeCard(it, idx, clone) {
    var card = document.createElement("figure");
    card.className = "pool-card";
    card.setAttribute("data-src", "assets/gallery/" + it.n + ".jpg");
    if (clone) card.setAttribute("aria-hidden", "true");
    card.style.setProperty("--ar", ratios[idx % ratios.length]);
    card.innerHTML =
      '<img loading="lazy" src="assets/gallery/' + it.n + '.jpg" alt="CDS project: ' + catLabel(it.cat) + '">' +
      '<span class="pool-cap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>' + catLabel(it.cat) + '</span>' +
      expandSvg;
    return card;
  }

  function setupRow(row, dir) {
    var track = row.querySelector(".pool-track");
    // 3 identical copies: keep scrollLeft in the MIDDLE copy [seg, 2*seg) so it
    // never touches the browser's 0/max clamp (that clamp caused the jitter).
    var seg = 0;
    function measure() { seg = track.scrollWidth / 3; }
    measure();
    track.querySelectorAll("img").forEach(function (im) { im.addEventListener("load", measure); });
    window.addEventListener("resize", measure);

    var seeded = false, dragging = false, startX = 0, startScroll = 0, moved = 0, speed = 0.5;
    function wrap() {
      if (seg <= 0) return;
      if (row.scrollLeft >= 2 * seg) row.scrollLeft -= seg;
      else if (row.scrollLeft < seg) row.scrollLeft += seg;
    }
    function frame() {
      if (seg > 0 && !seeded) { row.scrollLeft = seg; seeded = true; } // start in the middle copy
      if (!dragging && !reduceMotion && seg > 0) { row.scrollLeft += speed * dir; wrap(); }
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);

    // continuous loop: no hover pause; only manual drag interrupts the drift
    row.addEventListener("pointerdown", function (e) {
      dragging = true; moved = 0; startX = e.clientX; startScroll = row.scrollLeft;
      row.classList.add("dragging"); try { row.setPointerCapture(e.pointerId); } catch (_) {}
    });
    row.addEventListener("pointermove", function (e) {
      if (!dragging) return;
      var dx = e.clientX - startX; moved = Math.max(moved, Math.abs(dx));
      row.scrollLeft = startScroll - dx; wrap();
    });
    function end(e) { if (!dragging) return; dragging = false; row.classList.remove("dragging"); try { row.releasePointerCapture(e.pointerId); } catch (_) {} }
    row.addEventListener("pointerup", end);
    row.addEventListener("pointercancel", end);
    row.addEventListener("click", function (e) {
      if (moved > 6) { e.preventDefault(); return; } // was a drag, not a tap
      var card = e.target.closest(".pool-card");
      if (card) openLbSrc(card.getAttribute("data-src"));
    });
  }

  var poolRows = document.querySelectorAll(".pool-row");
  var perRow = Math.ceil(items.length / poolRows.length);
  poolRows.forEach(function (row, ri) {
    var track = row.querySelector(".pool-track");
    var set = items.slice(ri * perRow, (ri + 1) * perRow);
    if (!set.length) set = items;
    // triple the row's set so the loop can live in the middle copy (seamless, no edge clamp)
    for (var pass = 0; pass < 3; pass++) {
      set.forEach(function (it, idx) { track.appendChild(makeCard(it, idx, pass > 0)); });
    }
    setupRow(row, parseInt(row.getAttribute("data-dir"), 10) || 1);
  });

  /* ---------- Lightbox (shared, driven by src list) ---------- */
  var lb = document.getElementById("lightbox");
  var lbImg = document.getElementById("lbImg");
  var lbClose = document.getElementById("lbClose");
  var lbPrev = document.getElementById("lbPrev");
  var lbNext = document.getElementById("lbNext");
  var lbIndex = 0;
  function openLbSrc(src) {
    lbIndex = Math.max(0, srcs.indexOf(src));
    lbImg.setAttribute("src", srcs[lbIndex]);
    lb.classList.add("open"); lb.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }
  function closeLb() { lb.classList.remove("open"); lb.setAttribute("aria-hidden", "true"); document.body.style.overflow = ""; }
  function step(dir) { lbIndex = (lbIndex + dir + srcs.length) % srcs.length; lbImg.setAttribute("src", srcs[lbIndex]); }
  lbClose.addEventListener("click", closeLb);
  lbPrev.addEventListener("click", function () { step(-1); });
  lbNext.addEventListener("click", function () { step(1); });
  lb.addEventListener("click", function (e) { if (e.target === lb) closeLb(); });
  document.addEventListener("keydown", function (e) {
    if (!lb.classList.contains("open")) return;
    if (e.key === "Escape") closeLb();
    if (e.key === "ArrowLeft") step(-1);
    if (e.key === "ArrowRight") step(1);
  });

  /* ---------- Stat count-up (motivated: rewards reaching the proof band) ---------- */
  var statObserver = new IntersectionObserver(function (entries, obs) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      obs.unobserve(e.target);
      if (reduceMotion || qaMode) return;
      var b = e.target.querySelector("b");
      var full = b.innerHTML;
      var m = full.match(/^(\d+)/);
      if (!m) return;
      var target = parseInt(m[1], 10);
      var suffix = full.slice(m[1].length);
      var start = null, dur = 900;
      function tick(ts) {
        if (!start) start = ts;
        var p = Math.min((ts - start) / dur, 1);
        var val = Math.round((0.2 + 0.8 * (1 - Math.pow(1 - p, 3))) * target);
        b.innerHTML = val + suffix;
        if (p < 1) requestAnimationFrame(tick);
        else b.innerHTML = full;
      }
      requestAnimationFrame(tick);
    });
  }, { threshold: 0.5 });
  document.querySelectorAll(".stat").forEach(function (s) { statObserver.observe(s); });

  /* ---------- QA helper: instant jump to hash for screenshots ---------- */
  if (qaMode) {
    var heroEl = document.querySelector(".hero");
    if (heroEl) heroEl.style.minHeight = "720px"; // let full page stack for tall screenshots
  }

  /* ---------- Quote form (demo, no backend) ---------- */
  var form = document.getElementById("quoteForm");
  var ok = document.getElementById("formOk");
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var name = form.querySelector("#name");
    var phone = form.querySelector("#phone");
    var valid = true;
    [name, phone].forEach(function (f) {
      if (!f.value.trim()) { f.style.borderColor = "var(--accent)"; valid = false; }
      else { f.style.borderColor = ""; }
    });
    if (!valid) return;
    ok.classList.add("show");
    form.querySelector('button[type="submit"]').textContent = "Details captured";
  });
})();
