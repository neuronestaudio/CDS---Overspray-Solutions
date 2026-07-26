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

  /* ---------- Gallery data (32 real project photos) ---------- */
  // Loose service tagging so the filter reads sensibly across all real jobs.
  var cats = {
    coating: [15, 16, 24, 25, 31, 32],
    fleet: [26, 27, 28, 29, 30],
    detail: [] // fallback filled below
  };
  var items = [];
  for (var i = 1; i <= 32; i++) {
    var n = ("0" + i).slice(-2);
    var cat = "detail";
    if (cats.coating.indexOf(i) > -1) cat = "coating";
    else if (cats.fleet.indexOf(i) > -1) cat = "fleet";
    items.push({ n: n, cat: cat });
  }

  var gallery = document.getElementById("gallery");
  var frag = document.createDocumentFragment();
  var plus = '<span class="g-plus"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg></span>';
  items.forEach(function (it, idx) {
    var d = document.createElement("figure");
    d.className = "g-item";
    d.setAttribute("data-cat", it.cat);
    d.setAttribute("data-idx", idx);
    d.innerHTML = '<img loading="lazy" src="assets/gallery/' + it.n + '.jpg" alt="CDS detailing project ' + it.n + '">' + plus;
    frag.appendChild(d);
  });
  gallery.appendChild(frag);

  /* ---------- Filters ---------- */
  var filterBtns = document.querySelectorAll(".gal-filters button");
  filterBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      filterBtns.forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");
      var f = btn.getAttribute("data-filter");
      gallery.querySelectorAll(".g-item").forEach(function (el) {
        var show = f === "all" || el.getAttribute("data-cat") === f;
        el.classList.toggle("hide", !show);
      });
    });
  });

  /* ---------- Lightbox ---------- */
  var lb = document.getElementById("lightbox");
  var lbImg = document.getElementById("lbImg");
  var lbClose = document.getElementById("lbClose");
  var lbPrev = document.getElementById("lbPrev");
  var lbNext = document.getElementById("lbNext");
  var current = 0;

  function visibleItems() {
    return Array.prototype.slice.call(gallery.querySelectorAll(".g-item:not(.hide)"));
  }
  function openLb(idx) {
    current = idx;
    var list = visibleItems();
    var src = list[current].querySelector("img").getAttribute("src");
    lbImg.setAttribute("src", src);
    lb.classList.add("open");
    lb.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }
  function closeLb() { lb.classList.remove("open"); lb.setAttribute("aria-hidden", "true"); document.body.style.overflow = ""; }
  function step(dir) {
    var list = visibleItems();
    current = (current + dir + list.length) % list.length;
    lbImg.setAttribute("src", list[current].querySelector("img").getAttribute("src"));
  }
  gallery.addEventListener("click", function (e) {
    var item = e.target.closest(".g-item");
    if (!item) return;
    var list = visibleItems();
    openLb(list.indexOf(item));
  });
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
