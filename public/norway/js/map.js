/* Route map, driven by window.NORWAY_MAP set on each page. Stops are place coordinates
   (OpenStreetMap/Nominatim); lines are straight connections between stops, not real trails or roads. */
(function () {
  var cfg = window.NORWAY_MAP;
  var el = document.getElementById('map');
  if (!cfg || !el || typeof L === 'undefined') return;

  var byId = {};
  cfg.stops.forEach(function (s) { byId[s.id] = s.ll; });
  function path(ids) { return ids.map(function (i) { return byId[i]; }); }

  var map = L.map(el, { scrollWheelZoom: false, zoomControl: true });
  L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    maxZoom: 17,
    attribution: 'Map data © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, SRTM | Style © <a href="https://opentopomap.org">OpenTopoMap</a> (CC-BY-SA)'
  }).addTo(map);

  var styles = {
    drive: { color: '#6b7b83', weight: 3, dashArray: '7 7', opacity: .95 },
    hike: { color: '#c62a1f', weight: 5, opacity: .95 }
  };
  cfg.lines.forEach(function (l) { L.polyline(path(l.ids), styles[l.style]).addTo(map); });

  var secondary = [];
  cfg.stops.forEach(function (s) {
    var icon = L.divIcon({ className: '', html: '<div class="pin ' + s.type + '">' + s.label + '</div>', iconSize: null, iconAnchor: [16, 14] });
    var m = L.marker(s.ll, { icon: icon, title: s.name + ' (' + s.days + ')', keyboard: true });
    m.bindPopup('<strong>' + s.name + '</strong><br>' + s.days + '<br>' + s.note);
    if (s.minZoom) secondary.push({ marker: m, minZoom: s.minZoom, on: false });
    else m.addTo(map);
  });
  /* Secondary pins (optional minZoom in the page config) appear only once zoomed in, so crowded areas stay readable. */
  function syncPins() {
    var z = map.getZoom();
    secondary.forEach(function (p) {
      var on = z >= p.minZoom;
      if (on && !p.on) { p.marker.addTo(map); p.on = true; }
      if (!on && p.on) { map.removeLayer(p.marker); p.on = false; }
    });
  }
  map.on('zoomend', syncPins);

  var views = {};
  Object.keys(cfg.views).forEach(function (k) {
    var ids = cfg.views[k] || cfg.stops.map(function (s) { return s.id; });
    views[k] = L.latLngBounds(path(ids));
  });
  var buttons = document.querySelectorAll('.views button');
  function show(v) {
    map.fitBounds(views[v], { padding: [34, 34], maxZoom: 12 });
    Array.prototype.forEach.call(buttons, function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-view') === v)); });
  }
  Array.prototype.forEach.call(buttons, function (b) { b.addEventListener('click', function () { show(b.getAttribute('data-view')); }); });
  show(cfg.view || 'all');
  syncPins();
  el.addEventListener('click', function () { map.scrollWheelZoom.enable(); });
  el.addEventListener('mouseleave', function () { map.scrollWheelZoom.disable(); });
})();
