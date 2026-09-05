/* Overspray work coverflow: angled side cards, active centre, arrows / dots /
   drag / keyboard, auto-advancing (infinite). Vanilla, no deps. */
(function () {
  "use strict";
  var root = document.querySelector("[data-ospx]");
  if (!root) return;
  var track = root.querySelector("#ospxTrack");
  var cards = Array.prototype.slice.call(track.querySelectorAll(".ospx-card"));
  var n = cards.length;
  if (!n) return;
  var REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var active = 0, timer = null, visible = false;
  // default to the Paint Correction card (looks the strongest as the opener)
  for (var di = 0; di < n; di++) { if (/paint correction/i.test(cards[di].textContent)) { active = di; break; } }

  var curEl = root.querySelector("[data-ospx-cur]");
  var totalEl = root.querySelector("[data-ospx-total]");
  var dotsWrap = root.querySelector("#ospxDots");
  var pad = x => (x < 10 ? "0" : "") + x;
  if (totalEl) totalEl.textContent = pad(n);

  var dots = cards.map(function (_, i) {
    var d = document.createElement("button");
    d.className = "ospx-dot"; d.type = "button"; d.setAttribute("aria-label", "Example " + (i + 1));
    d.addEventListener("click", function () { go(i); });
    dotsWrap.appendChild(d); return d;
  });

  function spacing() { return innerWidth < 620 ? innerWidth * 0.8 : Math.min(innerWidth * 0.27, 330); }
  var SP = spacing();

  // hero background mirrors the active card image (crossfade between two layers)
  var bgLayers = Array.prototype.slice.call(root.querySelectorAll(".hero-bgimg"));
  var bgFront = -1;
  function setHeroBg(src) {
    if (!bgLayers.length || !src) return;
    var next = (bgFront + 1) % bgLayers.length;
    if (bgLayers[next].dataset.src === src) return;
    bgLayers[next].dataset.src = src;
    bgLayers[next].style.backgroundImage = "url('" + src + "')";
    bgLayers[next].style.opacity = "1";
    if (bgFront >= 0) bgLayers[bgFront].style.opacity = "0";
    bgFront = next;
  }

  function layout() {
    var half = Math.floor(n / 2);
    cards.forEach(function (card, i) {
      var off = ((i - active) % n + n) % n; if (off > half) off -= n;
      var abs = Math.abs(off);
      var isActive = off === 0;
      card.classList.toggle("active", isActive);
      var mob = innerWidth < 620;
      var x = off * SP;
      var rot = mob ? 0 : -off * 22;                                  // flat single-card slider on phones
      var sc = isActive ? 1 : (mob ? 0.86 : Math.max(0.66, 0.82 - (abs - 1) * 0.07));
      var op = abs > half ? 0 : (isActive ? 1 : (mob ? 0.24 : 0.55 - (abs - 1) * 0.12)); // dim side peeks, no text jumble
      card.style.transform = "translate(-50%,-50%) translateX(" + x + "px) rotateY(" + rot + "deg) scale(" + sc + ")";
      card.style.opacity = op;
      card.style.zIndex = 100 - abs;
      card.setAttribute("aria-hidden", isActive ? "false" : "true");
    });
    if (curEl) curEl.textContent = pad(active + 1);
    dots.forEach(function (d, i) { d.classList.toggle("on", i === active); });
    var im = cards[active] && cards[active].querySelector("img");
    if (im) setHeroBg(im.currentSrc || im.src);
  }

  function go(i) { active = ((i % n) + n) % n; layout(); restart(); }
  function next() { go(active + 1); }
  function prev() { go(active - 1); }

  root.querySelector(".ospx-next").addEventListener("click", next);
  root.querySelector(".ospx-prev").addEventListener("click", prev);
  cards.forEach(function (card, i) {
    card.addEventListener("click", function (e) { if (i !== active && !e.target.closest("a")) go(i); });
  });

  // drag / swipe
  var sx = 0, drag = false;
  track.addEventListener("pointerdown", function (e) { drag = true; sx = e.clientX; });
  addEventListener("pointerup", function (e) { if (!drag) return; drag = false; var dx = e.clientX - sx; if (dx < -44) next(); else if (dx > 44) prev(); });

  addEventListener("keydown", function (e) { if (!visible) return; if (e.key === "ArrowLeft") prev(); else if (e.key === "ArrowRight") next(); });
  addEventListener("resize", function () { SP = spacing(); layout(); });

  function restart() { if (timer) clearTimeout(timer); if (!REDUCED && visible) timer = setTimeout(next, 4400); }
  root.addEventListener("pointerenter", function () { if (timer) clearTimeout(timer); });
  root.addEventListener("pointerleave", restart);
  new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) restart(); else if (timer) clearTimeout(timer); }, { threshold: 0.2 }).observe(root);

  layout();
})();
