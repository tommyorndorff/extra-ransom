// Reads a Garmin Connect export (TCX or GPX) in the browser and works out the numbers the log form needs.
// Nothing is uploaded: the file is parsed locally and only the prefilled form values are used.
//
//   C25K_IMPORT.parseText(text, fileName) -> { date, distance_mi, duration_min, run_pct, basis, sport }
//   C25K_IMPORT.analyze(points)           -> { moving_sec, run_sec, run_pct, basis }   (exposed for tests)
//
// Running share is an estimate. Per ~12-second window it calls the stretch "running" when
//   - the file has cadence: cadence >= 135 steps/min and speed >= 1.5 m/s, otherwise
//   - no cadence: speed >= 2.0 m/s (about 13:25 per mile).
// Time standing still (speed under 0.4 m/s) is ignored.
(function () {
  var MILE = 1609.344, WINDOW = 12, MAX_GAP = 60;

  function fail(msg) { var e = new Error(msg); e.friendly = true; return e; }
  function kids(node, name) {
    var out = [];
    for (var c = node.firstElementChild; c; c = c.nextElementSibling) if (c.localName === name) out.push(c);
    return out;
  }
  function text(node, name) { var k = kids(node, name)[0]; return k ? k.textContent.trim() : null; }
  function all(node, name) { return Array.prototype.slice.call(node.getElementsByTagNameNS('*', name)); }
  function num(s) { var n = parseFloat(s); return isFinite(n) ? n : null; }
  function isoLocal(d) {
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }
  function haversine(a, b) {
    var R = 6371008.8, rad = Math.PI / 180;
    var dLat = (b.lat - a.lat) * rad, dLon = (b.lon - a.lon) * rad;
    var h = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(a.lat * rad) * Math.cos(b.lat * rad) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    return 2 * R * Math.asin(Math.sqrt(h));
  }
  function percentile(arr, p) {
    var s = arr.slice().sort(function (a, b) { return a - b; });
    return s[Math.min(s.length - 1, Math.floor(p * s.length))];
  }

  // points: [{ t: seconds, d: cumulative meters, cad: number|null }], sorted by t.
  function analyze(points) {
    if (points.length < 2) return { moving_sec: 0, run_sec: 0, run_pct: null, basis: null };
    var cads = points.map(function (p) { return p.cad; }).filter(function (c) { return c != null && c > 0; });
    var hasCad = cads.length >= points.length * 0.5;
    // Garmin exports cadence per leg (strides/min: ~80-90 running). Double it unless it already looks like steps/min.
    var factor = hasCad && percentile(cads, 0.95) <= 130 ? 2 : 1;
    var moving = 0, run = 0, j = 0;
    for (var i = 1; i < points.length; i++) {
      var dt = points[i].t - points[i - 1].t;
      if (dt <= 0 || dt > MAX_GAP) continue;
      while (j < i - 1 && points[i].t - points[j + 1].t >= WINDOW) j++;
      var span = points[i].t - points[j].t;
      var v = span > 0 ? (points[i].d - points[j].d) / span : 0;
      if (v < 0.4) continue;
      moving += dt;
      var running;
      if (hasCad && points[i].cad != null) running = points[i].cad * factor >= 135 && v >= 1.5;
      else running = v >= 2.0;
      if (running) run += dt;
    }
    var pct = moving >= 60 ? Math.round((100 * run / moving) / 5) * 5 : null;
    return { moving_sec: moving, run_sec: run, run_pct: pct, basis: hasCad ? 'cadence' : 'speed' };
  }

  function parseXml(textIn) {
    var doc = new DOMParser().parseFromString(textIn, 'application/xml');
    if (doc.getElementsByTagName('parsererror').length) throw fail('That file is not valid XML. Export the activity as TCX or GPX from Garmin Connect.');
    return doc;
  }

  function parseTcx(doc) {
    var act = all(doc, 'Activity')[0];
    if (!act) throw fail('No activity found in that TCX file.');
    var sport = act.getAttribute('Sport') || '';
    var laps = all(act, 'Lap');
    var lapDist = 0, lapSec = 0, startIso = laps.length ? laps[0].getAttribute('StartTime') : null;
    laps.forEach(function (l) { lapDist += num(text(l, 'DistanceMeters')) || 0; lapSec += num(text(l, 'TotalTimeSeconds')) || 0; });
    var points = [];
    all(act, 'Trackpoint').forEach(function (tp) {
      var t = text(tp, 'Time'), d = num(text(tp, 'DistanceMeters'));
      if (!t || d == null) return;
      var ms = Date.parse(t);
      if (isNaN(ms)) return;
      var cad = all(tp, 'RunCadence')[0];
      cad = cad ? num(cad.textContent) : num(text(tp, 'Cadence'));
      if (!startIso) startIso = t;
      points.push({ t: ms / 1000, d: d, cad: cad });
    });
    points.sort(function (a, b) { return a.t - b.t; });
    var dist = lapDist > 0 ? lapDist : (points.length ? points[points.length - 1].d - points[0].d : 0);
    var sec = lapSec > 0 ? lapSec : (points.length ? points[points.length - 1].t - points[0].t : 0);
    return { sport: sport, startIso: startIso, dist: dist, sec: sec, points: points };
  }

  function parseGpx(doc) {
    var trk = all(doc, 'trk')[0];
    if (!trk) throw fail('No track found in that GPX file. Export a recorded activity, not a course.');
    var sport = text(trk, 'type') || '';
    var raw = [];
    all(trk, 'trkpt').forEach(function (p) {
      var t = text(p, 'time'), lat = num(p.getAttribute('lat')), lon = num(p.getAttribute('lon'));
      if (!t || lat == null || lon == null) return;
      var ms = Date.parse(t);
      if (isNaN(ms)) return;
      var cad = all(p, 'cad')[0];
      raw.push({ t: ms / 1000, lat: lat, lon: lon, cad: cad ? num(cad.textContent) : null, iso: t });
    });
    raw.sort(function (a, b) { return a.t - b.t; });
    var points = [], cum = 0, sec = 0;
    raw.forEach(function (p, i) {
      if (i > 0) {
        var dt = p.t - raw[i - 1].t;
        if (dt > 0 && dt <= MAX_GAP) { cum += haversine(raw[i - 1], p); sec += dt; }
      }
      points.push({ t: p.t, d: cum, cad: p.cad });
    });
    return { sport: sport, startIso: raw.length ? raw[0].iso : null, dist: cum, sec: sec, points: points };
  }

  function parseText(textIn, fileName) {
    var name = (fileName || '').toLowerCase();
    if (/\.(fit|zip)$/.test(name)) throw fail('FIT and ZIP files are not supported yet. In Garmin Connect, use Export to TCX or Export to GPX instead.');
    var doc = parseXml(textIn), root = doc.documentElement.localName.toLowerCase(), r;
    if (root === 'trainingcenterdatabase') r = parseTcx(doc);
    else if (root === 'gpx') r = parseGpx(doc);
    else throw fail('That does not look like a TCX or GPX file.');
    if (!r.points.length || !(r.dist > 0) || !(r.sec > 0)) throw fail('That file has no distance or time data.');
    var start = r.startIso ? new Date(r.startIso) : null, a = analyze(r.points);
    return {
      date: start && !isNaN(start) ? isoLocal(start) : null,
      distance_mi: Math.round(r.dist / MILE * 100) / 100,
      duration_min: Math.round(r.sec / 60 * 10) / 10,
      run_pct: a.run_pct,
      basis: a.basis,
      sport: r.sport
    };
  }

  window.C25K_IMPORT = { parseText: parseText, analyze: analyze };
})();
