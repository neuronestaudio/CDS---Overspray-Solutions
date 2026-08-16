/* =========================================================================
   CDS · Before / After drag-to-reveal slider
   Pointer drag + keyboard. No dependencies.
   ========================================================================= */
(function () {
  "use strict";
  var frames = document.querySelectorAll("[data-ba] .ba-frame");
  frames.forEach(function (frame) {
    var pos = 50;
    function set(p) {
      pos = Math.max(0, Math.min(100, p));
      frame.style.setProperty("--pos", pos + "%");
      frame.setAttribute("aria-valuenow", Math.round(pos));
    }
    function fromEvent(e) {
      var r = frame.getBoundingClientRect();
      var cx = e.touches ? e.touches[0].clientX : e.clientX;
      set(((cx - r.left) / r.width) * 100);
    }
    var down = false;
    frame.addEventListener("pointerdown", function (e) {
      down = true;
      try { frame.setPointerCapture(e.pointerId); } catch (_) {}
      fromEvent(e); e.preventDefault();
    });
    frame.addEventListener("pointermove", function (e) { if (down) fromEvent(e); });
    function up(e) { down = false; try { frame.releasePointerCapture(e.pointerId); } catch (_) {} }
    frame.addEventListener("pointerup", up);
    frame.addEventListener("pointercancel", up);
    frame.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") { set(pos - 4); e.preventDefault(); }
      else if (e.key === "ArrowRight") { set(pos + 4); e.preventDefault(); }
      else if (e.key === "Home") { set(0); e.preventDefault(); }
      else if (e.key === "End") { set(100); e.preventDefault(); }
    });
    set(50);
  });
})();
