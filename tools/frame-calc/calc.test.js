const test = require('node:test');
const assert = require('node:assert');
const { parse, fmt, compute } = require('../../static/frame-calc/js/calc.js');

const base = { mat: false, face: 1.25, thick: 0.875, rabW: 0.375, rabD: 0.5, clear: 1 / 16, kerf: 0.125, stick: 72 };

test('parse', () => {
  assert.strictEqual(parse('15 5/8'), 15.625);
  assert.strictEqual(parse('15-5/8"'), 15.625);
  assert.strictEqual(parse('5/8'), 0.625);
  assert.strictEqual(parse('11½'), 11.5);
  assert.ok(isNaN(parse('abc')));
});

test('fmt', () => {
  assert.strictEqual(fmt(17.5), '17½″');
  assert.strictEqual(fmt(13.375), '13⅜″');
  assert.strictEqual(fmt(0.1875), '3/16″');
  assert.strictEqual(fmt(2), '2″');
  assert.strictEqual(fmt(5.3125), '5 5/16″');
});

test('plan frame matches picture-frame.md', () => {
  const r = compute({ ...base, artW: 15.625, artH: 11.5 });
  assert.deepStrictEqual(r.errors, []);
  assert.strictEqual(r.outside.w, 17.5);
  assert.strictEqual(r.outside.h, 13.375);
  assert.strictEqual(r.rabbetOpen.w, 15.75);
  assert.strictEqual(r.rabbetOpen.h, 11.625);
  assert.strictEqual(r.sight.w, 15);
  assert.strictEqual(r.sight.h, 10.875);
  assert.ok(Math.abs(r.diag - 19.58) < 0.01);
  assert.strictEqual(r.lip, 0.375);
});

test('mat: exterior = opening + borders, bottom heavier', () => {
  const r = compute({ ...base, mat: true, artW: 8, artH: 10, overlap: 0.25, bT: 2, bL: 2, bR: 2, bB: 2.5 });
  assert.strictEqual(r.opening.w, 7.5);
  assert.strictEqual(r.opening.h, 9.5);
  assert.strictEqual(r.matExt.w, 11.5);
  assert.strictEqual(r.matExt.h, 14);
  assert.strictEqual(r.glass.w, 11.5);
});

test('reload code round-trips, tolerating wraps and surrounding text', () => {
  const { encodeState, decodeState } = require('../../static/frame-calc/js/calc.js');
  const st = { name: 'Lake é photo', artW: '15 5/8', mat: true, bB: '2 1/2' };
  const code = encodeState(st);
  assert.match(code, /^FC1\.[A-Za-z0-9_-]+~$/);
  const wrapped = 'Reload code ' + code.replace(/(.{20})/g, '$1\n ') + ' page 2';
  assert.deepStrictEqual(decodeState(wrapped), st);
  assert.strictEqual(decodeState('no code here'), null);
  assert.strictEqual(decodeState('FC1.!!!~'), null);
});

test('rejects absurd sizes (> 10 ft) and warns on > 4 ft', () => {
  assert.ok(compute({ ...base, artW: 150, artH: 10 }).errors.some(e => /over 10 feet/.test(e)));
  assert.ok(compute({ ...base, artW: 119, artH: 10 }).errors.some(e => /over 10 feet/.test(e)), 'outside > 120 via frame stock');
  assert.ok(compute({ ...base, mat: true, artW: 10, artH: 10, overlap: .25, bT: 200, bL: 2, bR: 2, bB: 2 }).errors.length);
  assert.ok(compute({ ...base, artW: 10, artH: 10, stick: 300 }).errors.length);
  const w = compute({ ...base, artW: 60, artH: 40 });
  assert.deepStrictEqual(w.errors, []);
  assert.ok(w.warnings.some(x => /4 feet/.test(x)));
  assert.strictEqual(compute({ ...base, artW: 20, artH: 10 }).warnings.length, 0);
});

test('validation', () => {
  assert.ok(compute({ ...base, artW: 0, artH: 5 }).errors.length);
  assert.ok(compute({ ...base, mat: true, artW: 0.4, artH: 5, overlap: 0.25 }).errors.length);
  assert.ok(compute({ ...base, rabW: 1.5, artW: 5, artH: 7 }).errors.length);
});
