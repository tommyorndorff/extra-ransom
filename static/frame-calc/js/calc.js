// Picture-frame calculator math. Pure functions, no DOM; works in browser and Node.
// Geometry follows tools/woodworking/picture_frame_drawings.py:
//   rabbet opening = glass + 2*clearance
//   sight opening  = rabbet opening - 2*rabbet width
//   outside (long point) = sight opening + 2*face width
(function (root) {
  'use strict';

  var GLYPH = { 2: '⅛' /* placeholder, replaced below */ };
  // sixteenths -> glyph (eighths and above use Unicode fractions, odd sixteenths use a/16)
  GLYPH = { 2: '⅛', 4: '¼', 6: '⅜', 8: '½', 10: '⅝', 12: '¾', 14: '⅞' };

  // Parse "15 5/8", "15-5/8", "5/8", "15.625", "15″"; returns NaN if unparseable.
  function parse(s) {
    if (typeof s === 'number') return s;
    s = String(s == null ? '' : s).trim().replace(/[″"″]/g, '').replace(/ /g, ' ');
    var uni = { '¼': 0.25, '½': 0.5, '¾': 0.75, '⅛': 0.125, '⅜': 0.375, '⅝': 0.625, '⅞': 0.875 };
    var extra = 0;
    Object.keys(uni).forEach(function (g) {
      if (s.indexOf(g) >= 0) { extra += uni[g]; s = s.replace(g, ' '); }
    });
    s = s.trim();
    if (s === '' && extra) return extra;
    var m;
    if ((m = /^(\d+)[\s-]+(\d+)\/(\d+)$/.exec(s))) return +m[1] + m[2] / m[3] + extra;
    if ((m = /^(\d+)\/(\d+)$/.exec(s))) return m[1] / m[2] + extra;
    if (/^\d*\.?\d+$/.test(s)) return parseFloat(s) + extra;
    return NaN;
  }

  // Format inches rounded to the nearest 1/16, e.g. 17.5 -> 17½″
  function fmt(x) {
    if (!isFinite(x)) return '—';
    var neg = x < 0;
    var sx = Math.round(Math.abs(x) * 16);
    var whole = Math.floor(sx / 16), n = sx % 16;
    var frac = n === 0 ? '' : (GLYPH[n] || (n + '/16'));
    var out = n === 0 ? String(whole) : (whole === 0 ? frac : whole + (GLYPH[n] ? '' : ' ') + frac);
    return (neg ? '-' : '') + out + '″';
  }

  function dec(x) { return isFinite(x) ? (Math.round(x * 1000) / 1000).toFixed(3).replace(/0+$/, '').replace(/\.$/, '') + '″' : '—'; }

  function compute(i) {
    var errors = [], warnings = [];
    var mat = !!i.mat;
    var artW = i.artW, artH = i.artH;
    var face = i.face, thick = i.thick, rabW = i.rabW, rabD = i.rabD, clear = i.clear;
    // kerf and stick length are optional: undefined means blank (0); NaN means invalid text.
    var kerf = i.kerf == null ? 0 : i.kerf;
    var overlap = i.overlap, bT = i.bT, bL = i.bL, bR = i.bR, bB = i.bB;

    var req = [['Art width', artW], ['Art height', artH], ['Stock face width', face], ['Stock thickness', thick],
      ['Rabbet width', rabW], ['Rabbet depth', rabD], ['Glass clearance', clear]];
    if (mat) req.push(['Mat overlap', overlap], ['Mat top border', bT], ['Mat bottom border', bB], ['Mat left border', bL], ['Mat right border', bR]);
    var HINT = ' Use a positive number such as 15.5 or 15 1/2 (a . for decimals).';
    var bad = false;
    req.forEach(function (p) {
      if (!(p[1] >= 0)) { errors.push(p[0] + ' is missing or not valid.' + (bad ? '' : HINT)); bad = true; }
    });
    if (!(kerf >= 0)) errors.push('Saw kerf is not valid (leave blank for none).');
    if (i.stick != null && !(i.stick >= 0)) errors.push('Stick length is not valid (leave blank to skip the stock estimate).');
    if (errors.length) return { errors: errors };
    if (!(artW > 0) || !(artH > 0)) errors.push('Art size must be greater than zero.');
    if (errors.length) return { errors: errors };

    // Sanity limits: nothing here is plausibly over 10 ft (120"). Inputs are inches.
    var MAX = 120;
    req.forEach(function (p) {
      if (p[1] > MAX) errors.push(p[0] + ' is ' + fmt(p[1]) + ', over 10 feet. Check the units: everything is in inches.');
    });
    if (i.stick > 240) errors.push('Stick length is over 20 feet. Check the units: everything is in inches.');
    if (errors.length) return { errors: errors };
    if (artW > 48 || artH > 48) warnings.push('Art is over 4 feet on a side. Check the units: everything is in inches.');

    var openW = artW, openH = artH, extW = artW, extH = artH;
    if (mat) {
      openW = artW - 2 * overlap;
      openH = artH - 2 * overlap;
      if (!(openW > 0) || !(openH > 0)) errors.push('Mat overlap leaves no opening.');
      extW = openW + bL + bR;
      extH = openH + bT + bB;
    }
    var glassW = extW, glassH = extH;
    var rabOpenW = glassW + 2 * clear, rabOpenH = glassH + 2 * clear;
    var sightW = rabOpenW - 2 * rabW, sightH = rabOpenH - 2 * rabW;
    var outW = sightW + 2 * face, outH = sightH + 2 * face;
    var lip = thick - rabD, wall = face - rabW;

    if (outW > MAX || outH > MAX) errors.push('Frame would be ' + fmt(Math.max(outW, outH)) + ' on its longest side, over 10 feet. Check the inputs: everything is in inches.');
    if (rabW >= face) errors.push('Rabbet width must be less than the face width.');
    if (rabD >= thick) errors.push('Rabbet depth must be less than the stock thickness.');
    if (!(sightW > 0) || !(sightH > 0)) errors.push('Sight opening is zero or negative.');
    if (!errors.length) {
      var overlapPic = rabW - clear;
      if (overlapPic <= 0) warnings.push('Rabbet is no wider than the clearance: the lip would not hold the glass.');
      if (lip < 0.25) warnings.push('Front lip is only ' + fmt(lip) + ' thick.');
    }
    if (errors.length) return { errors: errors };

    var perimeter = 2 * outW + 2 * outH;
    var kerfAlong = kerf * Math.SQRT2;
    var total = perimeter + 4 * kerfAlong;
    var stick = i.stick > 0 ? i.stick : 0;

    return {
      errors: [], warnings: warnings, mat: mat,
      art: { w: artW, h: artH },
      opening: { w: openW, h: openH },
      matBorders: { t: bT, l: bL, r: bR, b: bB },
      matExt: { w: extW, h: extH },
      glass: { w: glassW, h: glassH },
      rabbetOpen: { w: rabOpenW, h: rabOpenH },
      sight: { w: sightW, h: sightH },
      outside: { w: outW, h: outH },
      lip: lip, wall: wall,
      diag: Math.sqrt(rabOpenW * rabOpenW + rabOpenH * rabOpenH),
      members: [
        { name: 'Rail (top/bottom)', qty: 2, outside: outW, rabbet: rabOpenW, sight: sightW },
        { name: 'Stile (left/right)', qty: 2, outside: outH, rabbet: rabOpenH, sight: sightH }
      ],
      stockTotal: total,
      sticks: stick ? Math.ceil(total / stick) : null
    };
  }

  // Reload code: "FC1." + base64url(JSON) + "~". No whitespace or '.' inside the payload, so it
  // survives PDF text extraction (line wraps, split text runs).
  function encodeState(o) {
    var b = btoa(unescape(encodeURIComponent(JSON.stringify(o))));
    return 'FC1.' + b.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '') + '~';
  }
  // Finds the first reload code in any text (whitespace tolerated) and returns the state, or null.
  function decodeState(text) {
    var m = /FC1\.([A-Za-z0-9_\-\s]+)~/.exec(String(text || ''));
    if (!m) return null;
    try {
      var b = m[1].replace(/\s+/g, '').replace(/-/g, '+').replace(/_/g, '/');
      while (b.length % 4) b += '=';
      var o = JSON.parse(decodeURIComponent(escape(atob(b))));
      return o && typeof o === 'object' ? o : null;
    } catch (e) { return null; }
  }

  var api = { parse: parse, fmt: fmt, dec: dec, compute: compute, encodeState: encodeState, decodeState: decodeState };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.FrameCalc = api;
})(typeof window !== 'undefined' ? window : this);
