/* Route map. Stops are place coordinates (OpenStreetMap/Nominatim); lines are straight
   connections between stops, not the real trails or roads. */
(function () {
  var el = document.getElementById('map');
  if (!el || typeof L === 'undefined') return;

  var stops = [
    { id: 'oslo', name: 'Oslo', days: 'Days 1, 13–14', label: '1', type: 'move', ll: [59.9133, 10.739], note: 'Arrive, pick up the car, fly home.' },
    { id: 'rena', name: 'Rena (Østerdalen)', days: 'Days 1–2', label: '1–2', type: 'fish', ll: [61.1328, 11.3722], note: 'Easy day and an optional Glomma evening.' },
    { id: 'rondvassbu', name: 'Rondvassbu', days: 'Days 3–4', label: '3–4', type: 'hike', ll: [61.8804, 9.796], note: 'Staffed hut on Rondvatnet, Rondane.' },
    { id: 'bjornhollia', name: 'Bjørnhollia', days: 'Days 4–5', label: '4–5', type: 'hike', ll: [61.8845, 10.0121], note: 'Staffed hut in southern Rondane. Walk out on day 5.' },
    { id: 'otta', name: 'Otta', days: 'Days 6–7', label: '6', type: 'fish', ll: [61.7712, 9.5353], note: 'Rest day, laundry, an evening on the Lågen/Otta.' },
    { id: 'gjendesheim', name: 'Gjendesheim', days: 'Day 7', label: '7', type: 'hike', ll: [61.4954, 8.8096], note: 'East end of Lake Gjende. Start of Besseggen.' },
    { id: 'memurubu', name: 'Memurubu', days: 'Day 8', label: '8', type: 'hike', ll: [61.4908, 8.6311], note: 'End of the Besseggen day.' },
    { id: 'gjendebu', name: 'Gjendebu', days: 'Day 9', label: '9', type: 'hike', ll: [61.4514, 8.4886], note: 'West end of Gjende. Boat or walk from Memurubu.' },
    { id: 'glitterheim', name: 'Glitterheim', days: 'Day 10', label: '10', type: 'hike', ll: [61.6226, 8.6327], note: 'Below Glittertind.' },
    { id: 'spiterstulen', name: 'Spiterstulen', days: 'Day 11', label: '11', type: 'hike', ll: [61.6258, 8.4046], note: 'Base for Galdhøpiggen. Last hut night.' },
    { id: 'lom', name: 'Lom', days: 'Day 12', label: '12', type: 'fish', ll: [61.7143, 8.4259], note: 'Stave church, bakery, an evening on the Bøvra or Otta.' }
  ];
  var byId = {};
  stops.forEach(function (s) { byId[s.id] = s.ll; });
  function path(ids) { return ids.map(function (i) { return byId[i]; }); }

  var map = L.map(el, { scrollWheelZoom: false, zoomControl: true });
  L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    maxZoom: 17,
    attribution: 'Map data © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, SRTM | Style © <a href="https://opentopomap.org">OpenTopoMap</a> (CC-BY-SA)'
  }).addTo(map);

  var drive = { color: '#6b7b83', weight: 3, dashArray: '7 7', opacity: .95 };
  var hike = { color: '#c62a1f', weight: 5, opacity: .95 };
  L.polyline(path(['oslo', 'rena', 'rondvassbu']), drive).addTo(map);
  L.polyline(path(['bjornhollia', 'otta', 'gjendesheim']), drive).addTo(map);
  L.polyline(path(['spiterstulen', 'lom', 'oslo']), drive).addTo(map);
  L.polyline(path(['rondvassbu', 'bjornhollia']), hike).addTo(map);
  L.polyline(path(['gjendesheim', 'memurubu', 'gjendebu', 'glitterheim', 'spiterstulen']), hike).addTo(map);

  stops.forEach(function (s) {
    var icon = L.divIcon({ className: '', html: '<div class="pin ' + s.type + '">' + s.label + '</div>', iconSize: null, iconAnchor: [16, 14] });
    var m = L.marker(s.ll, { icon: icon, title: s.name + ' (' + s.days + ')', keyboard: true }).addTo(map);
    m.bindPopup('<strong>' + s.name + '</strong><br>' + s.days + '<br>' + s.note);
  });

  function bounds(ids) { return L.latLngBounds(ids.map(function (i) { return byId[i]; })); }
  var views = {
    all: bounds(stops.map(function (s) { return s.id; })),
    parks: bounds(['rondvassbu', 'bjornhollia', 'otta', 'gjendesheim', 'memurubu', 'gjendebu', 'glitterheim', 'spiterstulen', 'lom']),
    rondane: bounds(['rondvassbu', 'bjornhollia']),
    jotun: bounds(['gjendesheim', 'memurubu', 'gjendebu', 'glitterheim', 'spiterstulen', 'lom'])
  };
  var buttons = document.querySelectorAll('.views button');
  function show(v) {
    map.fitBounds(views[v], { padding: [34, 34], maxZoom: 12 });
    Array.prototype.forEach.call(buttons, function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-view') === v)); });
  }
  Array.prototype.forEach.call(buttons, function (b) { b.addEventListener('click', function () { show(b.getAttribute('data-view')); }); });
  show('parks');
  el.addEventListener('click', function () { map.scrollWheelZoom.enable(); });
  el.addEventListener('mouseleave', function () { map.scrollWheelZoom.disable(); });
})();
