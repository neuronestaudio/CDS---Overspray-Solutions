/* =========================================================================
   CDS · Overspray Solutions - interactions
   No window scroll listeners. IntersectionObserver for nav + reveals.
   ========================================================================= */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var qaMode = /[?&]qa\b/.test(location.search); // reveals everything up-front for QA/screenshots

  /* ---------- Entry splash cleanup (fade handled in CSS) ---------- */
  var splash2 = document.getElementById("splash2");
  if (splash2) {
    var splashOff = document.documentElement.classList.contains("splash-off");
    if (qaMode || splashOff) {
      splash2.classList.add("done"); // already hidden (return visit) or QA: no animation
    } else {
      try { sessionStorage.setItem("cds_splash_seen", "1"); } catch (e) {} // seen this session
      setTimeout(function () { splash2.classList.add("done"); }, 3400);
    }
  }

  /* ---------- Video hero: cycling blocky service headline ---------- */
  (function () {
    var rot = document.querySelector("[data-vrot]");
    if (!rot) return;
    var words = Array.prototype.slice.call(rot.querySelectorAll(".vhero-word"));
    if (words.length < 2 || reduceMotion) return; // reduced motion: keep the first word static
    var i = 0;
    setInterval(function () {
      words[i].classList.remove("is-on");
      i = (i + 1) % words.length;
      words[i].classList.add("is-on");
    }, 3800);
  })();

  /* ---------- Nav glass on scroll (sentinel, not scroll listener) ---------- */
  var nav = document.getElementById("nav");
  var sentinel = document.createElement("div");
  sentinel.style.cssText = "position:absolute;top:0;left:0;width:1px;height:60px;pointer-events:none";
  document.body.prepend(sentinel);
  new IntersectionObserver(function (entries) {
    nav.classList.toggle("scrolled", !entries[0].isIntersecting);
  }, { threshold: 0 }).observe(sentinel);

  /* ---------- Hero A/B/C demo switcher (corner buttons + ?hero=) ---------- */
  var heroEl = document.querySelector(".hero");
  var heroImg = document.querySelector(".hero-media img");
  var heroSrc = { b: "assets/img/hero-b.png", c: "assets/img/hero-c.png" };
  var heroDefaultSrc = heroImg ? heroImg.getAttribute("src") : "";
  function applyHero(key) {
    if (!heroImg) return;
    heroEl.classList.remove("hero-a", "hero-b", "hero-c");
    heroImg.style.display = "";
    if (heroSrc[key]) {
      heroEl.classList.add("hero-" + key);
      heroImg.onerror = function () { heroImg.style.display = "none"; }; // gradient fallback
      heroImg.src = heroSrc[key];
    } else {
      key = "default";
      heroImg.onerror = null;
      heroImg.src = heroDefaultSrc;
    }
    document.querySelectorAll(".hero-switch button").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-hero") === key);
    });
    try {
      var u = new URL(location.href);
      if (key === "default") u.searchParams.delete("hero"); else u.searchParams.set("hero", key);
      history.replaceState(null, "", u);
    } catch (_) {}
  }
  document.querySelectorAll(".hero-switch button").forEach(function (b) {
    b.addEventListener("click", function () { applyHero(b.getAttribute("data-hero")); });
  });
  var heroParam = (location.search.match(/[?&]hero=([a-z0-9]+)/i) || [])[1];
  applyHero(heroParam || "default");

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
  var cats = { coating: [1, 6, 14, 27, 30, 31], correction: [4, 8, 19, 20, 23] };
  function catLabel(c) { return c === "coating" ? "Ceramic" : c === "correction" ? "Correction" : "Detailing"; }
  var items = [];
  for (var i = 1; i <= 32; i++) {
    var n = ("0" + i).slice(-2);
    var cat = "detail";
    if (cats.coating.indexOf(i) > -1) cat = "coating";
    else if (cats.correction.indexOf(i) > -1) cat = "correction";
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

    var seeded = false, dragging = false, startX = 0, startScroll = 0, moved = 0, speed = 1.05;
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
    var vheroEl = document.querySelector(".vhero");
    if (vheroEl) vheroEl.style.minHeight = "760px"; // same, for the video hero (100svh would eat tall windows)
  }

  /* ---------- CDS band: keyframed word reveal (Car / Detailing / Solutions) ---------- */
  (function () {
    var band = document.querySelector(".cds-para[data-parallax]");
    if (!band) return;
    if (reduceMotion || qaMode) { band.classList.add("lit"); return; }
    new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { band.classList.add("lit"); obs.unobserve(e.target); }
      });
    }, { threshold: 0.35 }).observe(band);
  })();

  /* ---------- Reviews carousel ---------- */
  (function () {
    var rev = document.querySelector("[data-rev]");
    if (!rev) return;
    var track = rev.querySelector(".rev-track");
    var cards = track.children;
    var total = cards.length;
    if (total <= 1) { var nav = rev.querySelector(".rev-nav"); if (nav) nav.style.display = "none"; return; }
    var dotsWrap = rev.querySelector(".rev-dots");
    var idx = 0, timer = null;

    for (var d = 0; d < total; d++) {
      var b = document.createElement("button");
      b.type = "button";
      b.setAttribute("aria-label", "Go to review " + (d + 1));
      (function (i) { b.addEventListener("click", function () { go(i, true); }); })(d);
      dotsWrap.appendChild(b);
    }
    var dots = dotsWrap.children;

    function render() {
      track.style.transform = "translateX(" + (-idx * 100) + "%)";
      for (var i = 0; i < total; i++) dots[i].classList.toggle("on", i === idx);
    }
    function go(n, user) {
      idx = (n + total) % total;
      render();
      if (user) restart();
    }
    function restart() {
      if (reduceMotion) return;
      clearInterval(timer);
      timer = setInterval(function () { go(idx + 1); }, 6500);
    }

    rev.querySelector(".rev-prev").addEventListener("click", function () { go(idx - 1, true); });
    rev.querySelector(".rev-next").addEventListener("click", function () { go(idx + 1, true); });
    rev.addEventListener("mouseenter", function () { clearInterval(timer); });
    rev.addEventListener("mouseleave", restart);

    // basic swipe on touch
    var sx = 0, sactive = false;
    rev.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; sactive = true; }, { passive: true });
    rev.addEventListener("touchend", function (e) {
      if (!sactive) return; sactive = false;
      var dx = e.changedTouches[0].clientX - sx;
      if (Math.abs(dx) > 40) go(idx + (dx < 0 ? 1 : -1), true);
    });

    render();
    restart();
  })();

  /* ---------- Coating process (four-stage interactive stepper) ---------- */
  (function () {
    var cp = document.querySelector("[data-cp]");
    if (!cp) return;
    var tabs = Array.prototype.slice.call(cp.querySelectorAll(".cp-tab"));
    var panels = Array.prototype.slice.call(cp.querySelectorAll(".cp-panel"));
    var prog = cp.querySelector(".cp-progress");
    var cur = 0, timer = null;
    function playVid(pnl, on) {
      var v = pnl.querySelector("video");
      if (!v) return;
      if (on && !reduceMotion) {
        try { v.currentTime = 0; var p = v.play(); if (p && p.catch) p.catch(function () {}); } catch (e) {}
      } else {
        try { v.pause(); } catch (e) {}
      }
    }
    function go(i, user) {
      cur = (i + tabs.length) % tabs.length;
      tabs.forEach(function (t, j) { var on = j === cur; t.classList.toggle("is-on", on); t.setAttribute("aria-selected", on ? "true" : "false"); });
      panels.forEach(function (pnl, j) { var on = j === cur; pnl.classList.toggle("is-on", on); playVid(pnl, on); });
      if (prog) prog.style.transform = "translateX(" + (cur * 100) + "%)";
      if (user) restart();
    }
    function restart() { if (reduceMotion) return; clearInterval(timer); timer = setInterval(function () { go(cur + 1); }, 5600); }
    tabs.forEach(function (t, i) { t.addEventListener("click", function () { go(i, true); }); });
    cp.addEventListener("mouseenter", function () { clearInterval(timer); });
    cp.addEventListener("mouseleave", restart);
    go(0); restart();
  })();

  /* ---------- Booking wizard lives in js/booking.js ---------- */
})();
