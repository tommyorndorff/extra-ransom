(function () {
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  var LEVEL_NAMES = { beginner: 'Starting from the couch', intermediate: 'Can run ~5 minutes', runner: 'Already running 20+ min' };
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function pd(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function shortDate(s) { var d = pd(s); return MON[d.getMonth()] + ' ' + d.getDate(); }
  function round(n, k) { var f = Math.pow(10, k); return Math.round(n * f) / f; }
  function total(s) { return s.segs.reduce(function (t, g) { return t + g.sec; }, 0); }
  function runSec(s) { return s.segs.reduce(function (t, g) { return t + (g.type === 'run' ? g.sec : 0); }, 0); }
  function pace(minutes, miles) {
    if (!miles || !minutes) return '';
    var p = minutes / miles, m = Math.floor(p), s = Math.round((p - m) * 60);
    if (s === 60) { m++; s = 0; }
    return m + ':' + String(s).padStart(2, '0') + ' /mi';
  }
  function banner(msg) { var b = document.getElementById('banner'); b.hidden = !msg; b.textContent = msg || ''; }

  // Simple SVG bar chart. series: [{label, a (actual or null), b (planned or null)}]
  function chart(title, rows, unit, max, fmtv) {
    var W = 520, H = 220, L = 34, B = 34, T = 14, R = 8, n = rows.length, pw = (W - L - R) / n;
    var svg = '<svg class="chart" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' + esc(title) + '">';
    [0, 0.5, 1].forEach(function (f) {
      var y = T + (H - T - B) * (1 - f);
      svg += '<line class="grid" x1="' + L + '" x2="' + (W - R) + '" y1="' + y + '" y2="' + y + '"/>' +
             '<text x="' + (L - 4) + '" y="' + (y + 4) + '" text-anchor="end">' + fmtv(max * f) + '</text>';
    });
    rows.forEach(function (r, i) {
      var x = L + pw * i, bw = pw * 0.36;
      function h(v) { return (H - T - B) * Math.min(1, v / max); }
      if (r.b != null) svg += '<rect class="bar-b" x="' + (x + pw * 0.1) + '" y="' + (H - B - h(r.b)) + '" width="' + bw + '" height="' + h(r.b) + '" rx="2"><title>Plan: ' + fmtv(r.b) + unit + '</title></rect>';
      if (r.a != null) svg += '<rect class="bar-a" x="' + (x + pw * 0.1 + bw + 2) + '" y="' + (H - B - h(r.a)) + '" width="' + bw + '" height="' + h(r.a) + '" rx="2"><title>Done: ' + fmtv(r.a) + unit + '</title></rect>';
      svg += '<text x="' + (x + pw / 2) + '" y="' + (H - B + 14) + '" text-anchor="middle">' + esc(r.label) + '</text>';
    });
    return svg + '</svg>';
  }

  C25K.open().then(function (store) {
    if (store.error === 'unknown') { banner('That link is not recognized. Check that you copied the whole thing.'); return; }
    if (store.error === 'network') { banner('Could not reach the server. Try again in a bit.'); return; }
    var sessions = PLAN.sessionsFor(store.level), entries = store.entries;
    document.getElementById('title').textContent = store.mode === 'remote' ? store.name + "'s progress" : 'Your progress';
    document.getElementById('lede').textContent = LEVEL_NAMES[store.level] + ' plan' + (store.mode === 'local' ? ' · saved on this device only' : '') + (store.mode === 'remote' && !store.canEdit ? ' · view only' : '');
    if (store.mode === 'remote') document.getElementById('back').href = '../?p=' + encodeURIComponent(store.token);

    var logged = sessions.filter(function (s) { return entries[s.id]; });
    var dist = 0, dur = 0, pairD = 0, pairT = 0, pcts = [], longest = 0;
    logged.forEach(function (s) {
      var e = entries[s.id];
      if (e.distance_mi != null) { dist += +e.distance_mi; longest = Math.max(longest, +e.distance_mi); }
      if (e.duration_min != null) dur += +e.duration_min;
      if (e.distance_mi != null && e.duration_min != null && +e.distance_mi > 0) { pairD += +e.distance_mi; pairT += +e.duration_min; }
      if (e.run_pct != null) pcts.push(+e.run_pct);
    });
    var avgPct = pcts.length ? Math.round(pcts.reduce(function (a, b) { return a + b; }, 0) / pcts.length) : null;

    var c = document.getElementById('content');
    var tiles = el('div', 'tiles');
    function tile(v, l) { tiles.appendChild(el('div', 'tile', '<strong>' + v + '</strong><span>' + l + '</span>')); }
    tile(logged.length + ' / ' + sessions.length, 'sessions logged');
    tile(dist ? round(dist, 1) + ' mi' : '–', 'total distance');
    tile(dur ? Math.round(dur) + ' min' : '–', 'total time');
    tile(pace(pairT, pairD) || '–', 'average pace');
    tile(avgPct != null ? avgPct + '%' : '–', 'average running share');
    tile(longest ? round(longest, 2) + ' mi' : '–', 'longest session');
    c.appendChild(tiles);

    // charts
    var rows1 = sessions.map(function (s, i) {
      var e = entries[s.id];
      return { label: s.race ? '🦃' : String(i + 1), a: e && e.distance_mi != null ? +e.distance_mi : null, b: null };
    });
    var maxD = Math.max(4, 2 * Math.ceil(Math.max.apply(null, rows1.map(function (r) { return r.a || 0; })) / 2));
    var rows2 = sessions.map(function (s, i) {
      var e = entries[s.id];
      return { label: s.race ? '🦃' : String(i + 1), a: e && e.run_pct != null ? +e.run_pct : null, b: Math.round(100 * runSec(s) / total(s)) };
    });
    var charts = el('div', 'charts');
    charts.appendChild(el('div', 'panel', '<h2>Distance per session</h2>' + chart('Distance per session in miles', rows1, ' mi', maxD, function (v) { return round(v, 1); }) + '<p class="hint">Session number across the bottom; the turkey is race day.</p>'));
    charts.appendChild(el('div', 'panel', '<h2>Running share</h2>' + chart('Percent of time running, planned versus actual', rows2, '%', 100, function (v) { return Math.round(v) + '%'; }) + '<p class="hint">Light bars are the plan, orange is what was logged.</p>'));
    c.appendChild(charts);

    // table
    var rows = sessions.map(function (s, i) {
      var e = entries[s.id], planned = Math.round(total(s) / 60) + ' min, ' + Math.round(100 * runSec(s) / total(s)) + '% run';
      if (!e) return '<tr class="skipped"><td>' + (i + 1) + '</td><td>' + shortDate(s.date) + '</td><td>' + esc(s.title) + '</td><td>' + planned + '</td><td colspan="5"><span class="pill">not logged</span></td></tr>';
      return '<tr><td>' + (i + 1) + '</td><td>' + shortDate(e.date) + '</td><td>' + esc(s.title) + '</td><td>' + planned + '</td>' +
        '<td>' + (e.distance_mi != null ? round(+e.distance_mi, 2) + ' mi' : '–') + '</td>' +
        '<td>' + (e.duration_min != null ? round(+e.duration_min, 1) + ' min' : '–') + '</td>' +
        '<td>' + (pace(e.duration_min, e.distance_mi) || '–') + '</td>' +
        '<td>' + (e.run_pct != null ? e.run_pct + '% run' : '–') + '</td>' +
        '<td class="n">' + (e.note ? esc(e.note) : '') + '</td></tr>';
    }).join('');
    var panel = el('div', 'panel');
    panel.innerHTML = '<h2>Session by session</h2><div class="tablewrap"><table class="log"><thead><tr><th>#</th><th>Date</th><th>Session</th><th>Plan</th><th>Distance</th><th>Time</th><th>Pace</th><th>Running</th><th>Notes</th></tr></thead><tbody>' + rows + '</tbody></table></div>';
    c.appendChild(panel);

    // notes timeline
    var withNotes = logged.filter(function (s) { return entries[s.id].note; });
    if (withNotes.length) {
      var np = el('div', 'panel'); np.appendChild(el('h2', null, 'Notes'));
      var ul = el('ul', 'notes-list');
      withNotes.slice().sort(function (a, b) { return entries[a.id].date < entries[b.id].date ? -1 : 1; }).forEach(function (s) {
        ul.appendChild(el('li', null, '<time>' + shortDate(entries[s.id].date) + ' · ' + esc(s.title) + '</time>' + esc(entries[s.id].note)));
      });
      np.appendChild(ul); c.appendChild(np);
    }
    if (store.mode === 'remote' && store.canEdit) c.appendChild(el('p', 'fine', 'Share this page: ask for your read-only link. The link you are using now can edit your log, so keep it private.'));
  });
})();
