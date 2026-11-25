(function () {
  'use strict';
  var C = window.FrameCalc;
  var $ = function (id) { return document.getElementById(id); };

  // Stock/rabbet defaults are the plan frame (picture-frame.md): 1 1/4 x 7/8 stock, 3/8 x 1/2 rabbet, 1/16 clearance.
  var STOCK = { face: '1 1/4', thick: '7/8', rabW: '3/8', rabD: '1/2', clear: '1/16', kerf: '1/8', stick: '72' };
  function p(o) { return Object.assign({ mat: false, overlap: '1/4', bT: '2', bL: '2', bR: '2', bB: '2 1/2', bBauto: true, bBextra: '1/2' }, STOCK, o); }

  var PRESETS = [
    { label: 'Plan frame 15⅝ × 11½ (no mat)', v: p({ artW: '15 5/8', artH: '11 1/2' }) },
    { label: '5 × 7, no mat', v: p({ artW: '7', artH: '5' }) },
    { label: '8 × 10, no mat', v: p({ artW: '10', artH: '8' }) },
    { label: '11 × 14, no mat', v: p({ artW: '14', artH: '11' }) },
    { label: '8 × 10, 2″ mat', v: p({ artW: '10', artH: '8', mat: true }) },
    { label: '11 × 14, 2½″ mat', v: p({ artW: '14', artH: '11', mat: true, bT: '2 1/2', bL: '2 1/2', bR: '2 1/2', bB: '3' }) },
    { label: 'Custom', v: null }
  ];

  var FIELDS = ['name', 'artW', 'artH', 'bT', 'bL', 'bR', 'bB', 'bBextra', 'overlap', 'face', 'thick', 'rabW', 'rabD', 'clear', 'kerf', 'stick'];
  var KEY = 'frame-calc-v1';

  function load(v) {
    FIELDS.forEach(function (f) { if (v[f] != null) $(f).value = v[f]; });
    $('mat').checked = !!v.mat;
    $('bBauto').checked = v.bBauto !== false;
    sync();
  }
  function read() {
    var o = {};
    FIELDS.forEach(function (f) { o[f] = $(f).value; });
    o.mat = $('mat').checked; o.bBauto = $('bBauto').checked;
    return o;
  }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(read())); } catch (e) { /* ignore */ } }

  function sync() {
    $('matFields').hidden = !$('mat').checked;
    var auto = $('bBauto').checked;
    $('bB').disabled = auto;
    if (auto) {
      var t = C.parse($('bT').value), x = C.parse($('bBextra').value);
      $('bB').value = (!isNaN(t) && !isNaN(x)) ? C.fmt(t + x).replace('″', '') : '';
    }
  }

  function esc(s) { return String(s).replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; }); }
  function cell(x) { return '<td class="n">' + C.fmt(x) + '<span class="dec">' + C.dec(x) + '</span></td>'; }
  function size(a) { return C.fmt(a.w).replace('″', '') + ' × ' + C.fmt(a.h); }

  function schematic(r) {
    var W = r.outside.w, H = r.outside.h, s = 360 / Math.max(W, H), pad = 10;
    var f = function (x) { return (x * s).toFixed(1); };
    var ox = pad, oy = pad, o = r.outside;
    var wall = (o.w - r.sight.w) / 2;
    var svg = '<svg viewBox="0 0 ' + (o.w * s + 2 * pad).toFixed(0) + ' ' + (o.h * s + 2 * pad).toFixed(0) + '" role="img" aria-label="Frame schematic" xmlns="http://www.w3.org/2000/svg">' +
      '<rect width="100%" height="100%" fill="#fff"/>' +
      '<rect x="' + ox + '" y="' + oy + '" width="' + f(o.w) + '" height="' + f(o.h) + '" fill="#e6d3b3" stroke="#333"/>' +
      '<rect x="' + (ox + wall * s).toFixed(1) + '" y="' + (oy + wall * s).toFixed(1) + '" width="' + f(r.sight.w) + '" height="' + f(r.sight.h) + '" fill="#fff" stroke="#333"/>';
    // 45 degree miters
    var ix = ox + wall * s, iy = oy + wall * s, ex = ox + o.w * s, ey = oy + o.h * s;
    svg += '<g stroke="#333" stroke-dasharray="3 3"><line x1="' + ox + '" y1="' + oy + '" x2="' + ix + '" y2="' + iy + '"/><line x1="' + ex + '" y1="' + oy + '" x2="' + (ix + r.sight.w * s) + '" y2="' + iy + '"/>' +
      '<line x1="' + ox + '" y1="' + ey + '" x2="' + ix + '" y2="' + (iy + r.sight.h * s) + '"/><line x1="' + ex + '" y1="' + ey + '" x2="' + (ix + r.sight.w * s) + '" y2="' + (iy + r.sight.h * s) + '"/></g>';
    if (r.mat) {
      var m = r.matBorders, rw = (r.rabbetOpen.w - r.matExt.w) / 2;
      var gx = ix - (r.rabbetOpen.w - r.sight.w) / 2 * s + rw * s;
      var gy = iy - (r.rabbetOpen.h - r.sight.h) / 2 * s + rw * s;
      svg += '<rect x="' + gx.toFixed(1) + '" y="' + gy.toFixed(1) + '" width="' + f(r.matExt.w) + '" height="' + f(r.matExt.h) + '" fill="#f4efe4" stroke="#999" stroke-dasharray="2 2"/>' +
        '<rect x="' + (gx + m.l * s).toFixed(1) + '" y="' + (gy + m.t * s).toFixed(1) + '" width="' + f(r.opening.w) + '" height="' + f(r.opening.h) + '" fill="#cfe0ee" stroke="#333"/>';
    }
    return svg + '</svg>';
  }

  // Optional numeric field: blank -> undefined, otherwise parsed (NaN if invalid).
  function opt(id) { var v = $(id).value.trim(); return v === '' ? undefined : C.parse(v); }

  function render() {
    sync(); save();
    var inp = {
      mat: $('mat').checked,
      artW: C.parse($('artW').value), artH: C.parse($('artH').value),
      bT: C.parse($('bT').value), bL: C.parse($('bL').value), bR: C.parse($('bR').value), bB: C.parse($('bB').value),
      overlap: C.parse($('overlap').value),
      face: C.parse($('face').value), thick: C.parse($('thick').value),
      rabW: C.parse($('rabW').value), rabD: C.parse($('rabD').value),
      clear: C.parse($('clear').value), kerf: opt('kerf'), stick: opt('stick')
    };

    var r = C.compute(inp);
    var name = $('name').value.trim();
    $('sTitle').textContent = name ? 'Picture frame — ' + name : 'Picture frame';
    $('sDate').textContent = new Date().toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });

    var errBox = $('errors');
    if (r.errors.length) {
      errBox.innerHTML = r.errors.map(function (e) { return '<p>' + esc(e) + '</p>'; }).join('');
      $('sheetBody').innerHTML = '';
      $('summary').hidden = true;
      return;
    }
    errBox.innerHTML = (r.warnings || []).map(function (e) { return '<p class="warn">' + esc(e) + '</p>'; }).join('');

    $('summary').hidden = false;
    $('summary').innerHTML = '<strong>Frame outside ' + size(r.outside) + '</strong>' +
      (r.mat ? ' &middot; mat ' + size(r.matExt) + ' with opening ' + size(r.opening) : ' &middot; glass ' + size(r.glass)) +
      ' &middot; <a href="#sheet">Jump to cut sheet &darr;</a>';

    var h = '';
    h += '<h3>Frame members (45° miters)</h3><table><thead><tr><th>Piece</th><th class="n">Qty</th>' +
      '<th class="n">Outside<br>(long pt)</th><th class="n">Inside at sight<br>(short pt)</th><th class="n">Inside at rabbet</th></tr></thead><tbody>';
    r.members.forEach(function (m) {
      h += '<tr><td>' + m.name + '</td><td class="n">' + m.qty + '</td>' + cell(m.outside) + cell(m.sight) + cell(m.rabbet) + '</tr>';
    });
    h += '</tbody></table>';
    h += '<p class="muted">Rails run along the width, stiles along the height. Lengths are point to point: <strong>outside</strong> is long point to long point, <strong>inside at sight</strong> is short point to short point along the visible opening. Cut every piece to its outside length; the inside lengths are for checking the dry fit. Rabbet is cut before mitering.</p>';

    h += '<h3>Cut list</h3><table><thead><tr><th>Qty</th><th>Piece</th><th class="n">Thickness</th><th class="n">Width</th><th class="n">Length (long point)</th></tr></thead><tbody>';
    r.members.forEach(function (m) {
      h += '<tr><td>' + m.qty + '</td><td>' + m.name + '</td>' + cell(inp.thick) + cell(inp.face) + cell(m.outside) + '</tr>';
    });
    h += '</tbody></table>';
    h += '<p>Total long-point length ' + C.fmt(2 * r.outside.w + 2 * r.outside.h) + ' (' + C.fmt(r.stockTotal) + ' with ' + C.fmt(inp.kerf) + ' kerf per cut)' +
      (r.sticks ? ' — about ' + r.sticks + ' × ' + C.fmt(inp.stick) + ' stick' + (r.sticks > 1 ? 's' : '') + ' before alternating miters and defects.' : '.') + '</p>';

    h += '<h3>Bill of materials</h3>';
    if (r.mat) {
      h += '<p class="bom-mat">Mat exterior size ' + size(r.matExt) + ' with mat opening of ' + size(r.opening) + '</p>';
    }
    var rows = [];
    function row(item, qty, sz, note) { rows.push('<tr><td><strong>' + item + '</strong></td><td class="n">' + qty + '</td><td>' + sz + '</td><td>' + note + '</td></tr>'); }
    if (r.mat) {
      row('Mat', 1, size(r.matExt), 'Opening ' + size(r.opening) + '. Borders: top ' + C.fmt(r.matBorders.t) + ', bottom ' + C.fmt(r.matBorders.b) +
        ', left ' + C.fmt(r.matBorders.l) + ', right ' + C.fmt(r.matBorders.r) + '.');
      row('Art', 1, size(r.art), 'Overlaps the opening by ' + C.fmt(inp.overlap) + ' per side.');
      row('Glass', 1, size(r.glass), 'Same as mat exterior.');
    } else {
      row('Art', 1, size(r.art), 'No mat.');
      row('Glass', 1, size(r.glass), 'Same as art.');
    }
    row('Backing', 1, size(r.glass), '⅛″ hardboard, thin ply or foam-core.');
    row('Frame stock', 4, C.fmt(inp.thick) + ' × ' + C.fmt(inp.face), 'Pieces per cut list. Rabbet ' + C.fmt(inp.rabW) + ' wide × ' + C.fmt(inp.rabD) + ' deep.');
    row('Retainers', '6–8', '—', 'Flexi-points or turn buttons.');
    row('Hanger', 1, '—', 'Two D-rings with wire, or one sawtooth hanger.');
    h += '<table class="bom"><thead><tr><th>Item</th><th class="n">Qty</th><th>Size (W × H)</th><th>Notes</th></tr></thead><tbody>' + rows.join('') + '</tbody></table>';

    h += '<h3>Key dimensions</h3><div class="sheet-inputs">' +
      '<div>Frame outside: <strong>' + size(r.outside) + '</strong></div>' +
      '<div>Sight opening: ' + size(r.sight) + '</div>' +
      '<div>Rabbet opening: ' + size(r.rabbetOpen) + '</div>' +
      '<div>Rabbet diagonals (square check): ' + C.fmt(r.diag) + ' (' + C.dec(r.diag) + ')</div>' +
      '<div>Front lip: ' + C.fmt(r.lip) + ' thick</div>' +
      '<div>Wall behind lip: ' + C.fmt(r.wall) + '</div></div>';

    h += '<h3>Sketch</h3>' + schematic(r);
    h += '<p class="reload">Reload code (paste or open this PDF at extra-ransom.net/frame-calc/): <span class="code">' + C.encodeState(read()) + '</span></p>';
    $('sheetBody').innerHTML = h;
  }

  // preset list
  PRESETS.forEach(function (pr, i) {
    var o = document.createElement('option'); o.value = i; o.textContent = pr.label; $('preset').appendChild(o);
  });
  $('preset').addEventListener('change', function () {
    var pr = PRESETS[+this.value];
    if (pr.v) { var keep = $('name').value; load(pr.v); $('name').value = keep; }
    render();
  });
  $('form').addEventListener('input', function (e) { if (e.target.id !== 'preset') { $('preset').value = PRESETS.length - 1; } render(); });
  $('form').addEventListener('change', render);
  $('print').addEventListener('click', function () { window.print(); });

  // ---- reload from a saved PDF or pasted code ----
  var PDFJS = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/';
  function msg(t, bad) { var m = $('importMsg'); m.textContent = t; m.style.color = bad ? 'var(--bad)' : ''; }
  var REQUIRED = ['artW', 'artH', 'face', 'thick', 'rabW', 'rabD', 'clear'];
  function apply(state) {
    if (!state) { msg('No frame calculator reload code found.', true); return false; }
    var missing = REQUIRED.filter(function (k) { return !(C.parse(state[k]) >= 0); });
    if (missing.length) { msg('That code is incomplete or damaged (bad: ' + missing.join(', ') + ').', true); return false; }
    load(state); $('preset').value = PRESETS.length - 1; render();
    msg('Loaded' + (state.name ? ': ' + state.name : '') + '.');
    return true;
  }
  function loadPdfJs() {
    if (window.pdfjsLib) return Promise.resolve(window.pdfjsLib);
    return new Promise(function (ok, fail) {
      var s = document.createElement('script');
      s.src = PDFJS + 'pdf.min.js';
      s.onload = function () { window.pdfjsLib.GlobalWorkerOptions.workerSrc = PDFJS + 'pdf.worker.min.js'; ok(window.pdfjsLib); };
      s.onerror = function () { fail(new Error('Could not load the PDF reader (offline?). Paste the code instead.')); };
      document.head.appendChild(s);
    });
  }
  $('codeIn').addEventListener('input', function () {
    var v = this.value.trim();
    if (!v) { msg(''); return; }
    if (v.indexOf('~') < 0) { msg('Keep going: the code ends with ~'); return; }
    if (apply(C.decodeState(v))) this.value = '';
  });
  $('pdfFile').addEventListener('change', function () {
    var f = this.files && this.files[0];
    if (!f) return;
    msg('Reading PDF…');
    Promise.all([loadPdfJs(), f.arrayBuffer()]).then(function (a) {
      return a[0].getDocument({ data: a[1] }).promise;
    }).then(function (doc) {
      var pages = [];
      for (var n = 1; n <= doc.numPages; n++) {
        pages.push(doc.getPage(n).then(function (pg) {
          return pg.getTextContent().then(function (tc) { return tc.items.map(function (it) { return it.str; }).join(''); });
        }));
      }
      return Promise.all(pages);
    }).then(function (texts) { apply(C.decodeState(texts.join('\n'))); })
      .catch(function (e) { msg(e && e.message ? e.message : 'Could not read that PDF.', true); });
    this.value = '';
  });

  var saved = null;
  try { saved = JSON.parse(localStorage.getItem(KEY)); } catch (e) { saved = null; }
  if (saved && saved.artW) { load(saved); $('preset').value = PRESETS.length - 1; } else { load(PRESETS[0].v); }
  render();
})();
