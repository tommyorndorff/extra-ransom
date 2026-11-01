(function () {
  var apiBase = '/api/c25k';
  try {
    var o = new URLSearchParams(location.search).get('api');
    if (o && /^http:\/\/localhost:\d+\//.test(o) && /^(localhost|127\.0\.0\.1)$/.test(location.hostname)) apiBase = o.replace(/\/$/, '');
  } catch (e) {}
  var key = '';
  try { key = sessionStorage.getItem('c25k-admin') || ''; } catch (e) {}
  var $ = function (id) { return document.getElementById(id); };
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function banner(m) { $('banner').hidden = !m; $('banner').textContent = m || ''; }
  var base = location.origin + location.pathname.replace(/admin\/?$/, '');
  var dev = apiBase !== '/api/c25k' ? '&api=' + encodeURIComponent(apiBase) : '';

  function call(method, path, body) {
    return fetch(apiBase + path, { method: method, headers: { 'x-admin-key': key, 'content-type': 'application/json' }, body: body ? JSON.stringify(body) : undefined })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { if (!r.ok) throw new Error(j.error || ('HTTP ' + r.status)); return j; }); });
  }
  function editUrl(t) { return base + '?p=' + t + dev; }
  function viewUrl(t) { return base + 'summary/?p=' + t + dev; }
  function copy(text, btn) {
    var done = function () { var o = btn.textContent; btn.textContent = 'Copied'; setTimeout(function () { btn.textContent = o; }, 1200); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () { prompt('Copy this link:', text); });
    else prompt('Copy this link:', text);
  }

  function load() {
    return call('GET', '/people').then(function (j) {
      banner('');
      $('addForm').hidden = false; $('list').hidden = false;
      var list = $('list');
      list.innerHTML = '<h2>' + j.people.length + ' ' + (j.people.length === 1 ? 'person' : 'people') + '</h2>';
      if (!j.people.length) list.appendChild(Object.assign(document.createElement('p'), { textContent: 'Nobody yet. Add the first person above.' }));
      j.people.forEach(function (p) {
        var row = document.createElement('div'); row.className = 'adminrow';
        row.innerHTML = '<div><i class="dot" style="background:' + esc(p.color) + '"></i><strong>' + esc(p.name) + '</strong><small>' + esc(p.level) + ' · ' + p.entries + ' sessions logged</small></div><div class="linkbtns"></div>';
        var box = row.querySelector('.linkbtns');
        [['Copy edit link', function (b) { copy(editUrl(p.edit_token), b); }],
         ['Copy view link', function (b) { copy(viewUrl(p.view_token), b); }],
         ['Open', function () { window.open(editUrl(p.edit_token), '_blank', 'noopener'); }],
         ['Delete', function () {
            if (!confirm('Delete ' + p.name + ' and all of their logged sessions? This cannot be undone.')) return;
            call('DELETE', '/people/' + p.id).then(load).catch(function (e) { banner(e.message); });
         }]].forEach(function (a) {
          var b = document.createElement('button'); b.type = 'button'; b.className = 'btn small'; b.textContent = a[0];
          b.addEventListener('click', function () { a[1](b); }); box.appendChild(b);
        });
        list.appendChild(row);
      });
    }).catch(function (e) {
      $('addForm').hidden = true; $('list').hidden = true;
      banner(e.message === 'admin key required' ? 'That admin key was not accepted.' : 'Could not load people: ' + e.message);
    });
  }

  $('keyForm').addEventListener('submit', function (ev) {
    ev.preventDefault(); key = $('key').value;
    try { sessionStorage.setItem('c25k-admin', key); } catch (e) {}
    load();
  });
  $('addForm').addEventListener('submit', function (ev) {
    ev.preventDefault();
    call('POST', '/people', { name: $('name').value, level: $('level').value })
      .then(function () { $('name').value = ''; return load(); })
      .catch(function (e) { banner(e.message); });
  });
  if (key) { $('key').value = key; load(); }
})();
