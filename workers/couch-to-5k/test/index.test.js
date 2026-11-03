import test from 'node:test';
import assert from 'node:assert/strict';
import { parseEntry, safeEqual, cleanName, newToken, cleanColor, colorOf, PALETTE, parseDay } from '../src/index.js';

test('parseEntry accepts a full entry and rounds run_pct', () => {
  const r = parseEntry({ date: '2026-11-02', distance_mi: '2.1', duration_min: 32, run_pct: 59.6, note: '  felt good ' });
  assert.deepEqual(r.value, { date: '2026-11-02', distance_mi: 2.1, duration_min: 32, run_pct: 60, note: 'felt good' });
});

test('parseEntry treats blank optional fields as null', () => {
  const r = parseEntry({ date: '2026-11-02', distance_mi: '', duration_min: null, note: '   ' });
  assert.deepEqual(r.value, { date: '2026-11-02', distance_mi: null, duration_min: null, run_pct: null, note: null });
});

test('parseEntry rejects bad input', () => {
  assert.ok(parseEntry(null).error);
  assert.ok(parseEntry({}).error);
  assert.ok(parseEntry({ date: '11/02/2026' }).error);
  assert.ok(parseEntry({ date: '2026-13-45' }).error);
  assert.ok(parseEntry({ date: '2026-11-02', run_pct: 101 }).error);
  assert.ok(parseEntry({ date: '2026-11-02', distance_mi: -1 }).error);
  assert.ok(parseEntry({ date: '2026-11-02', duration_min: 'abc' }).error);
  assert.ok(parseEntry({ date: '2026-11-02', note: 'x'.repeat(1001) }).error);
});

test('safeEqual compares strings of any length', () => {
  assert.equal(safeEqual('abc', 'abc'), true);
  assert.equal(safeEqual('abc', 'abd'), false);
  assert.equal(safeEqual('abc', 'abcd'), false);
  assert.equal(safeEqual('', ''), true);
});

test('cleanName trims, collapses spaces, and limits length', () => {
  assert.equal(cleanName('  Tom   O  '), 'Tom O');
  assert.equal(cleanName(''), null);
  assert.equal(cleanName('x'.repeat(41)), null);
  assert.equal(cleanName(42), null);
});

test('newToken is url-safe and unique', () => {
  const a = newToken(), b = newToken();
  assert.match(a, /^[A-Za-z0-9_-]{32}$/);
  assert.notEqual(a, b);
});

test('cleanColor accepts #rrggbb only and lowercases it', () => {
  assert.equal(cleanColor('#D9591F'), '#d9591f');
  assert.equal(cleanColor(' #2f7fb8 '), '#2f7fb8');
  assert.equal(cleanColor('red'), null);
  assert.equal(cleanColor('#fff'), null);
  assert.equal(cleanColor('#12345g'), null);
  assert.equal(cleanColor('url(javascript:1)'), null);
  assert.equal(cleanColor(7), null);
});

test('colorOf prefers the chosen color and otherwise cycles the palette', () => {
  assert.equal(colorOf({ id: 3, color: '#112233' }), '#112233');
  assert.equal(colorOf({ id: 1, color: null }), PALETTE[0]);
  assert.equal(colorOf({ id: PALETTE.length + 1, color: null }), PALETTE[0]);
});

test('parseDay needs a plan-period date and two booleans', () => {
  assert.deepEqual(parseDay('2026-11-05', { strength: true, sauna: false }).value, { strength: true, sauna: false, yoga: false, bike: null });
  assert.equal(parseDay('2026-11-05', { strength: false, sauna: false, yoga: true }).value.yoga, true);
  assert.ok(parseDay('2026-11-05', { strength: false, sauna: false, yoga: 'yes' }).error);
  assert.equal(parseDay('2026-11-05', { strength: false, sauna: false, bike: 'indoor' }).value.bike, 'indoor');
  assert.equal(parseDay('2026-11-05', { strength: false, sauna: false, bike: 'outdoor' }).value.bike, 'outdoor');
  assert.ok(parseDay('2026-11-05', { strength: false, sauna: false, bike: 'treadmill' }).error);
  assert.ok(parseDay('2026-11-5', { strength: true, sauna: true }).error);
  assert.ok(parseDay('2026-02-30', { strength: true, sauna: true }).error);
  assert.ok(parseDay('2025-01-01', { strength: true, sauna: true }).error);
  assert.ok(parseDay('2026-11-05', { strength: 'yes', sauna: true }).error);
  assert.ok(parseDay('2026-11-05', { strength: true }).error);
  assert.ok(parseDay('2026-11-05', null).error);
});
