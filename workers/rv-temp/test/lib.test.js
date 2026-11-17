import test from 'node:test';
import assert from 'node:assert/strict';
import { parseReading, evaluate, diffAlerts, buildEmail } from '../src/lib.js';

const cfg = { lowTempF: 37, highTempF: 95, lowRailV: 11.8, lowBattV: 3.5, missedMin: 150 };
const row = (o) => ({ ts: 1000, temp_f: 70, rail_v: 12.8, ...o });

test('parseReading accepts a normal report and defaults the device', () => {
  const r = parseReading({ temp_f: 70.5, rail_v: 12.7, batt_v: 4.05, rssi: -83.4, lat: 35.6, lon: -82.5 });
  assert.deepEqual(r.value, { device: 'rv', temp_f: 70.5, rail_v: 12.7, batt_v: 4.05, rssi: -83, lat: 35.6, lon: -82.5 });
});

test('parseReading turns the DS18B20 fault value (-196.6 F) into a null temp', () => {
  assert.equal(parseReading({ temp_f: -196.6, rail_v: 12.5 }).value.temp_f, null);
});

test('parseReading rejects bad input', () => {
  assert.ok(parseReading(null).error);
  assert.ok(parseReading({ device: 'Bad Name', temp_f: 40 }).error);
  assert.ok(parseReading({ temp_f: 70, rail_v: 99 }).error);
  assert.ok(parseReading({ temp_f: 70, lat: 35 }).error);
  assert.ok(parseReading({}).error);
  assert.ok(parseReading({ temp_f: -196.6 }).error); // fault with nothing else to report
});

test('evaluate: normal reading has no conditions', () => {
  assert.ok(Object.values(evaluate(row(), 1060, cfg)).every((v) => v === null));
});

test('evaluate: freeze, heat, sag, and fault', () => {
  assert.match(evaluate(row({ temp_f: 35.6 }), 1060, cfg).low_temp, /35\.6 F, at or below 37 F/);
  assert.match(evaluate(row({ temp_f: 96 }), 1060, cfg).high_temp, /96\.0 F/);
  assert.match(evaluate(row({ rail_v: 11.5 }), 1060, cfg).low_rail, /11\.50 V/);
  assert.ok(evaluate(row({ temp_f: null }), 1060, cfg).sensor_fault);
});

test('evaluate: low_batt only when running without 12V', () => {
  assert.match(evaluate(row({ rail_v: null, batt_v: 3.4 }), 1060, cfg).low_batt, /3\.40 V/);
  assert.equal(evaluate(row({ rail_v: 12.8, batt_v: 3.4 }), 1060, cfg).low_batt, null);
  assert.equal(evaluate(row({ rail_v: null, batt_v: 3.9 }), 1060, cfg).low_batt, null);
});

test('evaluate: a stale reading only raises no_checkin', () => {
  const c = evaluate(row({ temp_f: 34 }), 1000 + 151 * 60, cfg);
  assert.ok(c.no_checkin);
  assert.equal(c.low_temp, null);
  assert.ok(Object.values(evaluate(null, 5000, cfg)).every((v) => v === null));
});

test('diffAlerts notifies on change, reminds late, clears on recovery', () => {
  const cond = { low_temp: 'cold', low_rail: null };
  assert.deepEqual(diffAlerts(cond, {}, 100, 3600).send, [{ kind: 'low_temp', msg: 'cold', type: 'new' }]);
  assert.deepEqual(diffAlerts(cond, { low_temp: 90 }, 100, 3600), { send: [], cleared: [] });
  assert.equal(diffAlerts(cond, { low_temp: 90 }, 4000, 3600).send[0].type, 'reminder');
  assert.deepEqual(diffAlerts({ low_temp: null }, { low_temp: 90 }, 100, 3600).cleared, ['low_temp']);
});

test('buildEmail strips header injection and has the needed headers', () => {
  const m = buildEmail({ from: 'a@x.net', to: 'b@y.com', subject: 'hi\r\nBcc: evil@z.com', text: 'body', id: 'abc' });
  assert.ok(!/\r\nBcc:/.test(m));
  assert.match(m, /^From: RV Sensor <a@x\.net>\r\nTo: b@y\.com\r\n/);
  assert.match(m, /Message-ID: <abc@x\.net>/);
});

