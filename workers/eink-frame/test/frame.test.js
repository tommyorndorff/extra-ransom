import test from 'node:test';
import assert from 'node:assert/strict';
import {
  latin1Safe, localParts, parseSlots, planWake, wmo, parseWeather, cleanPoem, pickBody, linecountFor, validTz,
} from '../src/frame.js';
import { parseDevice, parseMessage, parseTelemetry, newToken } from '../src/index.js';
import { FALLBACK_POEMS } from '../src/poems.js';

test('latin1Safe maps typography and drops what the fonts cannot draw', () => {
  assert.equal(latin1Safe('It’s “fine”—really…'), 'It\'s "fine" - really...');
  assert.equal(latin1Safe('café naïve °F'), 'café naïve °F');
  assert.equal(latin1Safe('6:02 AM'), '6:02 AM');
  assert.equal(latin1Safe('Dvořák \u{1F600}'), 'Dvorák ');
  assert.equal(latin1Safe('a\tb'), 'ab');
  assert.equal(latin1Safe(null), '');
});

test('localParts gives the local date, minutes and labels', () => {
  const now = new Date('2026-11-22T11:02:00Z');             // 6:02 AM in New York (EST)
  const p = localParts(now, 'America/New_York');
  assert.equal(p.date, '2026-11-22');
  assert.equal(p.minutes, 6 * 60 + 2);
  assert.equal(p.dateLabel, 'Sunday, November 22');
  assert.equal(p.timeLabel, 'Sun 6:02 AM');
  assert.equal(localParts(new Date('2026-11-22T03:00:00Z'), 'America/Los_Angeles').date, '2026-11-21');
});

test('validTz accepts IANA zones only', () => {
  assert.equal(validTz('Europe/Oslo'), true);
  assert.equal(validTz('Not/AZone'), false);
  assert.equal(validTz(''), false);
});

test('parseSlots sorts, dedupes and rejects junk', () => {
  assert.deepEqual(parseSlots('17:00, 06:00,06:00'), [360, 1020]);
  assert.equal(parseSlots('6am'), null);
  assert.equal(parseSlots(''), null);
  assert.equal(parseSlots('24:00'), null);
});

test('planWake sleeps to the next slot and absorbs early wakes', () => {
  const slots = [360, 1020];                                 // 06:00, 17:00
  assert.deepEqual(planWake(362, slots), { sleepS: (1020 - 362) * 60, effectiveMin: 362 });
  // woke 15 min early for 17:00: treat as 17:00, sleep to 06:00 tomorrow (13h15m)
  const early = planWake(1005, slots);
  assert.equal(early.effectiveMin, 1020);
  assert.equal(early.sleepS, (1440 + 360 - 1005) * 60);
  // late evening: next is 06:00 tomorrow
  assert.equal(planWake(1380, slots).sleepS, (1440 + 360 - 1380) * 60);
  // a single slot a day is capped at 16 h; the frame wakes, gets a short sleep and lands on time
  assert.equal(planWake(420, [360]).sleepS, 16 * 3600);
  // a wake just past midnight for a 23:50 slot is unaffected; 10 min minimum sleep
  assert.ok(planWake(0, [5]).sleepS >= 600);
});

test('wmo maps weather codes to icons', () => {
  assert.equal(wmo(0).icon, 'clear');
  assert.equal(wmo(3).icon, 'cloudy');
  assert.equal(wmo(53).icon, 'drizzle');
  assert.equal(wmo(63).icon, 'rain');
  assert.equal(wmo(75).icon, 'snow');
  assert.equal(wmo(95).icon, 'storm');
  assert.equal(wmo(1234).icon, 'cloudy');
});

test('parseWeather picks today or tomorrow and rounds', () => {
  const om = { daily: { weather_code: [51, 0], temperature_2m_max: [57.7, 61.2], temperature_2m_min: [48.9, 40.4], precipitation_probability_max: [53, 0] } };
  assert.deepEqual(parseWeather(om, false, 'F'), { label: 'Today', icon: 'drizzle', text: 'Drizzle', hi: 58, lo: 49, unit: 'F', pop: 53 });
  assert.equal(parseWeather(om, true, 'F').icon, 'clear');
  assert.equal(parseWeather({}, false, 'F'), null);
});

test('cleanPoem keeps short poems and rejects ones that will not fit', () => {
  const ok = cleanPoem({ title: 'T’s', author: 'A', lines: ['one', '', 'two', '', ''] });
  assert.deepEqual(ok, { title: "T's", author: 'A', lines: ['one', '', 'two'] });
  assert.equal(cleanPoem({ title: 'T', author: 'A', lines: Array(17).fill('x') }), null);
  assert.equal(cleanPoem({ title: 'T', author: 'A', lines: ['x'.repeat(71)] }), null);
  assert.equal(cleanPoem({ title: '', author: 'A', lines: ['x'] }), null);
  for (const p of FALLBACK_POEMS) assert.ok(cleanPoem(p), `fallback "${p.title}" must fit`);
});

test('linecountFor stays within 4..14 and varies by attempt', () => {
  for (let i = 0; i < 4; i++) { const n = linecountFor('2026-11-22', i); assert.ok(n >= 4 && n <= 14); }
  assert.notEqual(linecountFor('2026-11-22', 0), linecountFor('2026-11-22', 1));
});

test('pickBody: dated message beats pinned beats poem', () => {
  const poem = { title: 'P', author: 'A', lines: ['l'] };
  const msgs = [
    { body: 'pinned', from_name: null, show_on: null, pinned: 1, created_at: '2026-11-01 00:00:00' },
    { body: 'birthday', from_name: 'Tommy', show_on: '2026-11-22', pinned: 0, created_at: '2026-11-02 00:00:00' },
  ];
  assert.deepEqual(pickBody(msgs, '2026-11-22', poem), { kind: 'message', text: 'birthday', from: 'Tommy' });
  assert.equal(pickBody(msgs, '2026-11-23', poem).text, 'pinned');
  assert.deepEqual(pickBody([], '2026-11-23', poem), { kind: 'poem', ...poem });
});

test('parseDevice validates and normalises', () => {
  const r = parseDevice({ name: '  Mom  ', place: 'Asheville', lat: '35.59825', lon: -82.5623, tz: 'America/New_York', refresh: '17:00,06:00' });
  assert.deepEqual(r.value, { name: 'Mom', place: 'Asheville', lat: 35.5983, lon: -82.5623, tz: 'America/New_York', refresh: '06:00,17:00' });
  assert.ok(parseDevice({ name: 'x', lat: 95, lon: 0, tz: 'UTC' }).error);
  assert.ok(parseDevice({ name: 'x', lat: 0, lon: 0, tz: 'Mars/Base' }).error);
  assert.ok(parseDevice({ name: 'x', lat: null, lon: 0, tz: 'UTC' }).error);
  assert.deepEqual(parseDevice({ units: 'C' }, true).value, { units: 'C' });
  assert.ok(parseDevice({ units: 'K' }, true).error);
});

test('parseMessage: dated messages cannot also be pinned', () => {
  assert.deepEqual(parseMessage({ body: ' Hi ', show_on: '2026-12-25', pinned: true }).value,
    { body: 'Hi', from_name: null, show_on: '2026-12-25', pinned: 0 });
  assert.equal(parseMessage({ body: 'Hi', pinned: true }).value.pinned, 1);
  assert.ok(parseMessage({ body: '' }).error);
  assert.ok(parseMessage({ body: 'x'.repeat(401) }).error);
  assert.ok(parseMessage({ body: 'x', show_on: '12/25' }).error);
});

test('parseTelemetry ignores malformed headers', () => {
  const h = new Headers({ 'x-battery-mv': '3987', 'x-rssi': '-61', 'x-fw': '1.0.0' });
  assert.deepEqual(parseTelemetry(h), { battery_mv: 3987, rssi: -61, fw: '1.0.0' });
  const bad = new Headers({ 'x-battery-mv': '99999', 'x-rssi': 'abc', 'x-fw': '<script>' });
  assert.deepEqual(parseTelemetry(bad), { battery_mv: null, rssi: null, fw: null });
});

test('newToken is 20 unambiguous characters', () => {
  const t = newToken();
  assert.match(t, /^[a-km-np-z2-9]{20}$/);
  assert.notEqual(t, newToken());
});
