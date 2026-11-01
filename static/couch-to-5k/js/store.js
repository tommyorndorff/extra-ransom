// Storage for the Couch to Turkey Trot page. Two modes behind one interface:
//   remote: the page was opened with ?p=<token>; data lives in the Worker/D1 API.
//   local:  no token; data lives in this browser's localStorage.
// C25K.open() resolves to { mode, canEdit, name, level, entries, error, token,
//   setLevel(l), save(planId, entry), remove(planId) }. Entries are keyed by plan id:
//   { date, distance_mi, duration_min, run_pct, note } (each number/note may be null).
(function () {
  var LOCAL_KEY = 'c25k-trot-2026-v2', OLD_KEY = 'c25k-trot-2026';

  // patch: { strength?: bool, sauna?: bool, bike?: null | 'indoor' | 'outdoor' }
  function dayMerge(cur, patch) {
    return {
      strength: patch.strength === undefined ? !!cur.strength : !!patch.strength,
      sauna: patch.sauna === undefined ? !!cur.sauna : !!patch.sauna,
      bike: patch.bike === undefined ? (cur.bike || null) : patch.bike
    };
  }

  function qs(name) {
    try { return new URLSearchParams(location.search).get(name); } catch (e) { return null; }
  }
  var apiBase = '/api/c25k';
  // For local development only: ?api=http://localhost:8787/api/c25k
  var override = qs('api');
  if (override && /^http:\/\/localhost:\d+\//.test(override) && /^(localhost|127\.0\.0\.1)$/.test(location.hostname)) apiBase = override.replace(/\/$/, '');

  function request(method, path, token, body) {
    var headers = { 'x-token': token };
    if (body !== undefined) headers['content-type'] = 'application/json';
    return fetch(apiBase + path, { method: method, headers: headers, body: body === undefined ? undefined : JSON.stringify(body) })
      .then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (j) {
          if (!r.ok) { var e = new Error(j.error || ('HTTP ' + r.status)); e.status = r.status; throw e; }
          return j;
        });
      });
  }

  function openRemote(token) {
    var store = { mode: 'remote', token: token, canEdit: false, name: '', level: 'beginner', entries: {}, days: {}, error: null };
    return request('GET', '/me', token).then(function (j) {
      store.name = j.person.name; store.level = j.person.level; store.color = j.person.color; store.canEdit = j.person.can_edit;
      j.entries.forEach(function (e) { store.entries[e.plan_id] = e; });
      (j.days || []).forEach(function (d) { store.days[d.date] = { strength: d.strength, sauna: d.sauna, bike: d.bike || null }; });
      store.setLevel = function (level) {
        return request('PATCH', '/me', token, { level: level }).then(function () { store.level = level; });
      };
      store.setColor = function (color) {
        return request('PATCH', '/me', token, { color: color }).then(function (r) { store.color = r.color; });
      };
      // patch: { strength?: bool, sauna?: bool }; both false clears the day
      store.setDay = function (date, patch) {
        var cur = store.days[date] || { strength: false, sauna: false, bike: null };
        var next = dayMerge(cur, patch);
        return request('PUT', '/days/' + date, token, next).then(function () {
          if (next.strength || next.sauna || next.bike) store.days[date] = next; else delete store.days[date];
        });
      };
      store.save = function (planId, entry) {
        return request('PUT', '/entries/' + planId, token, entry).then(function (r) {
          store.entries[planId] = { plan_id: planId, date: r.date, distance_mi: r.distance_mi, duration_min: r.duration_min, run_pct: r.run_pct, note: r.note };
        });
      };
      store.remove = function (planId) {
        return request('DELETE', '/entries/' + planId, token).then(function () { delete store.entries[planId]; });
      };
      return store;
    }).catch(function (e) {
      store.error = e.status === 401 ? 'unknown' : 'network';
      store.canEdit = false;
      store.setLevel = store.setColor = store.setDay = store.save = store.remove = function () { return Promise.reject(e); };
      return store;
    });
  }

  function openLocal() {
    var data = { level: 'beginner', entries: {}, days: {} };
    try {
      var raw = localStorage.getItem(LOCAL_KEY);
      if (raw) data = JSON.parse(raw) || data;
      else {
        // migrate the first version, which only kept check marks
        var old = JSON.parse(localStorage.getItem(OLD_KEY) || '{}') || {};
        var dates = {};
        window.PLAN.sessionsFor('beginner').forEach(function (s) { dates[s.id] = s.date; });
        Object.keys(old.done || old).forEach(function (id) {
          if (dates[id] && (old.done ? old.done[id] : old[id])) data.entries[id] = { plan_id: id, date: dates[id], distance_mi: null, duration_min: null, run_pct: null, note: null };
        });
      }
    } catch (e) {}
    if (window.PLAN.levels.indexOf(data.level) < 0) data.level = 'beginner';
    if (!data.days) data.days = {};
    function persist() { try { localStorage.setItem(LOCAL_KEY, JSON.stringify(data)); } catch (e) {} return Promise.resolve(); }
    var store = { mode: 'local', token: null, canEdit: true, name: '', error: null, level: data.level, entries: data.entries, days: data.days };
    store.setLevel = function (level) { data.level = level; store.level = level; return persist(); };
    store.setDay = function (date, patch) {
      var cur = data.days[date] || { strength: false, sauna: false, bike: null };
      var next = dayMerge(cur, patch);
      if (next.strength || next.sauna || next.bike) data.days[date] = next; else delete data.days[date];
      return persist();
    };
    store.save = function (planId, entry) { data.entries[planId] = Object.assign({ plan_id: planId }, entry); return persist(); };
    store.remove = function (planId) { delete data.entries[planId]; return persist(); };
    store.reset = function () { data.entries = {}; data.days = {}; store.entries = data.entries; store.days = data.days; return persist(); };
    return Promise.resolve(store);
  }

  // Public, anonymous view of everyone: [{color, level, sessions, distance_mi, duration_min, run_pct}]
  function team() {
    return fetch(apiBase + '/team').then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    }).then(function (j) { return j.people; });
  }

  window.C25K = {
    token: qs('p'),
    team: team,
    // Dot colors people can pick from (they can also choose any color).
    palette: ['#d9591f', '#2f7fb8', '#3f9e5b', '#b04fb4', '#e0a31b', '#d6456b', '#2fa7a0', '#7a5cc8', '#8a6a3b', '#5b6b7a'],
    open: function () { var t = qs('p'); return t ? openRemote(t) : openLocal(); }
  };
})();
