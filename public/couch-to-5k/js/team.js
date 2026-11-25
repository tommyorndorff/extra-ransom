(function () {
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function round(n, k) { var f = Math.pow(10, k); return Math.round(n * f) / f; }
  var ids = PLAN.sessionsFor('beginner').map(function (s) { return s.id; });
  var LEVEL = { beginner: 'from the couch', intermediate: 'running ~5 min', runner: 'regular runner' };

  C25K.team().then(function (people) {
    var c = document.getElementById('content');
    if (!people.length) { c.appendChild(el('p', 'hint', 'Nobody has joined yet.')); return; }
    var totD = 0, totS = 0;
    people.forEach(function (p) { totD += p.distance_mi; totS += p.sessions.length; });
    var tiles = el('div', 'tiles');
    [[people.length, 'runners'], [totS, 'sessions logged'], [round(totD, 1) + ' mi', 'miles together']].forEach(function (t) {
      tiles.appendChild(el('div', 'tile', '<strong>' + t[0] + '</strong><span>' + t[1] + '</span>'));
    });
    c.appendChild(tiles);

    var panel = el('div', 'panel');
    panel.appendChild(el('h2', null, 'Sessions logged'));
    var grid = el('div', 'team');
    var head = el('div', 'trow head', '<span></span>' + ids.map(function (id, i) { return '<span>' + (id === 'race' ? '🦃' : i + 1) + '</span>'; }).join('') + '<span class="tot"></span>');
    grid.appendChild(head);
    people.forEach(function (p, n) {
      var row = el('div', 'trow');
      row.appendChild(el('span', null, '<i class="dot" style="background:' + p.color + '"></i>'));
      row.lastChild.title = 'Runner ' + (n + 1) + ' (' + LEVEL[p.level] + ')';
      ids.forEach(function (id) {
        var on = p.sessions.indexOf(id) >= 0, cell = el('span', 'c' + (on ? ' on' : '') + (id === 'race' ? ' race' : ''));
        if (on) { cell.style.background = p.color; cell.style.color = p.color; }
        cell.setAttribute('aria-label', 'Runner ' + (n + 1) + ', session ' + (ids.indexOf(id) + 1) + (on ? ' logged' : ' not logged'));
        row.appendChild(cell);
      });
      var bits = [p.sessions.length + ' of ' + ids.length];
      if (p.distance_mi) bits.push(round(p.distance_mi, 1) + ' mi');
      if (p.run_pct != null) bits.push(p.run_pct + '% run');
      row.appendChild(el('span', 'tot', bits.join(' · ')));
      grid.appendChild(row);
    });
    panel.appendChild(grid);
    panel.appendChild(el('p', 'hint', 'Run share is the average share of time spent running in logged sessions.'));
    c.appendChild(panel);
  }).catch(function () {
    var b = document.getElementById('banner'); b.hidden = false;
    b.textContent = 'Could not load the team view right now. Try again in a bit.';
  });
})();
