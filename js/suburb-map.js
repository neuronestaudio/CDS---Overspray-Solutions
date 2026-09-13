/* Suburb boundary map — draws the suburb's real gazetted outline on OpenStreetMap
   tiles via Leaflet. Leaflet is pulled from a CDN only once the map is near the
   viewport, since it sits below the fold on every suburb page. Each page inlines
   only its own geometry, so no page pays for the whole service area. */
(function () {
  var LEAFLET_CSS = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css";
  var LEAFLET_JS  = "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js";
  var pending = null;

  function ensureLeaflet() {
    if (window.L) return Promise.resolve();
    if (pending) return pending;
    pending = new Promise(function (resolve, reject) {
      var css = document.createElement("link");
      css.rel = "stylesheet"; css.href = LEAFLET_CSS;
      document.head.appendChild(css);
      var s = document.createElement("script");
      s.src = LEAFLET_JS;
      s.onload = function () { resolve(); };
      s.onerror = function () { reject(new Error("leaflet failed")); };
      document.head.appendChild(s);
    });
    return pending;
  }

  function draw(el) {
    var geo, bbox;
    try {
      geo = JSON.parse(el.getAttribute("data-geo"));
      bbox = JSON.parse(el.getAttribute("data-bbox"));
    } catch (e) { el.classList.add("is-failed"); return; }
    var colour = el.getAttribute("data-colour") || "#e11d2a";

    ensureLeaflet().then(function () {
      var map = L.map(el, {
        scrollWheelZoom: false,
        zoomControl: true,
        attributionControl: true
      });
      // Standard OpenStreetMap tiles (no API key). They are inverted to a dark
      // basemap in CSS — the filter is applied to the tile images only, so the
      // red boundary overlay keeps its real colour.
      L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 18,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map);
      var layer = L.geoJSON(geo, {
        style: { color: colour, weight: 2.5, opacity: .95, fillColor: colour, fillOpacity: .14 }
      }).addTo(map);
      try {
        map.fitBounds(layer.getBounds(), { padding: [16, 16] });
      } catch (e) {
        if (bbox) map.fitBounds([[bbox[1], bbox[0]], [bbox[3], bbox[2]]], { padding: [16, 16] });
      }
      el.classList.add("is-ready");
      // the container is sized by CSS, but Leaflet needs a nudge after layout
      setTimeout(function () { map.invalidateSize(); }, 120);
    }).catch(function () { el.classList.add("is-failed"); });
  }

  var nodes = document.querySelectorAll(".suburb-map__canvas");
  if (!nodes.length) return;
  if (!("IntersectionObserver" in window)) {
    for (var i = 0; i < nodes.length; i++) draw(nodes[i]);
    return;
  }
  var io = new IntersectionObserver(function (entries, obs) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { obs.unobserve(e.target); draw(e.target); }
    });
  }, { rootMargin: "250px" });
  for (var j = 0; j < nodes.length; j++) io.observe(nodes[j]);
})();
