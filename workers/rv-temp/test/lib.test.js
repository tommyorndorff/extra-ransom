import test from 'node:test';
import assert from 'node:assert/strict';
import { parseReading, parseDevices, deviceCfg, sessionStart, evaluate, diffAlerts, isOneShot, titleOf, buildEmail } from '../src/lib.js';

const cfg = { lowTempF: 37, highTempF: 95, lowRailV: 4.5, lowBattV: 3.5, missedMin: 150 };
const base = { ...cfg, hystF: 2 };
const row = (o) => ({ ts: 1000, temp_f: 70, rail_v: 5.0, ...o });

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
  assert.match(evaluate(row({ rail_v: 0.1 }), 1060, cfg).low_rail, /0\.10 V/);
  assert.ok(evaluate(row({ temp_f: null }), 1060, cfg).sensor_fault);
});

test('evaluate: low_batt only when running without external power', () => {
  assert.match(evaluate(row({ rail_v: null, batt_v: 3.4 }), 1060, cfg).low_batt, /3\.40 V/);
  assert.match(evaluate(row({ rail_v: 0, batt_v: 3.4 }), 1060, cfg).low_batt, /3\.40 V/);   // power lost and cell draining
  assert.equal(evaluate(row({ rail_v: 5.0, batt_v: 3.4 }), 1060, cfg).low_batt, null);   // powered: cell is charging
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


// ---- per-device profiles ----

const devices = { sauna: { label: 'Sauna', profile: 'sauna', targetF: 170, missedMin: 40 } };
const sauna = deviceCfg(base, devices, 'sauna'); // onF 120, hot 215, long 120 min, 60 s cadence by default

test('parseDevices: empty, valid, and malformed JSON never throw', () => {
  assert.deepEqual(parseDevices(undefined), { devices: {} });
  assert.deepEqual(parseDevices('{"a":{}}').devices, { a: {} });
  assert.ok(parseDevices('{nope').error);
  assert.deepEqual(parseDevices('{nope').devices, {});
  assert.ok(parseDevices('[1]').error);
});

test('deviceCfg: fallback to globals, label defaults, overrides, bad values ignored', () => {
  assert.equal(deviceCfg(base, {}, 'rv').label, 'RV');
  assert.equal(deviceCfg(base, {}, 'garage').label, 'garage');
  assert.equal(deviceCfg(base, {}, 'rv').lowTempF, 37);
  const c = deviceCfg(base, { rv: { label: 'Camper', lowTempF: '40', highTempF: 'hot', profile: 'weird' } }, 'rv');
  assert.equal(c.label, 'Camper');
  assert.equal(c.lowTempF, 40);
  assert.equal(c.highTempF, 95);
  assert.equal(c.profile, 'default');
  assert.equal(sauna.missedMin, 40);
  assert.equal(sauna.hotLimitF, 215);
  assert.equal(sauna.lowRailV, 4.5);
});

test('labels in titles; default RV wording unchanged', () => {
  assert.equal(titleOf('low_temp', 'RV'), 'RV too cold');
  assert.equal(titleOf('sauna_hot', 'Sauna'), 'Sauna too hot');
  assert.equal(titleOf('no_checkin'), 'RV sensor offline');
  assert.match(evaluate(row({ temp_f: 35 }), 1060, { ...base, label: 'Camper' }).low_temp, /^Camper is 35\.0 F/);
});

test('hysteresis: a reading hovering at the limit does not flap', () => {
  const c = { ...base, label: 'RV' };
  assert.ok(evaluate(row({ temp_f: 36 }), 1060, c).low_temp);                              // trips at 37
  assert.equal(evaluate(row({ temp_f: 38 }), 1060, c).low_temp, null);                     // not active: 38 is fine
  assert.ok(evaluate(row({ temp_f: 38 }), 1060, c, [], { low_temp: 900 }).low_temp);       // active: holds until 39+
  assert.equal(evaluate(row({ temp_f: 39.5 }), 1060, c, [], { low_temp: 900 }).low_temp, null);
  assert.ok(evaluate(row({ temp_f: 94 }), 1060, c, [], { high_temp: 900 }).high_temp);
  assert.equal(evaluate(row({ temp_f: 92 }), 1060, c, [], { high_temp: 900 }).high_temp, null);
});

// A run of 60 s readings starting at ts0 with the given temps (newest first).
const run = (ts0, temps) => temps.map((t, i) => ({ ts: ts0 + i * 60, temp_f: t })).reverse();
const at = (h) => ({ ...h[0], rail_v: null });

test('sauna: cold is normal, no low/high temp alerts', () => {
  const c = evaluate({ ts: 1000, temp_f: 60, rail_v: null }, 1060, sauna, []);
  assert.ok(Object.values(c).every((v) => v === null));
  assert.equal(evaluate({ ts: 1000, temp_f: 130, rail_v: null }, 1060, sauna, []).high_temp, null);
});

test('sauna_ready fires once per session and re-arms after cooling below onF', () => {
  const h = run(1000, [130, 160, 171]);
  const c1 = evaluate(at(h), h[0].ts, sauna, h, {});
  assert.match(c1.sauna_ready, /Sauna reached 171\.0 F/);
  assert.deepEqual(diffAlerts(c1, {}, 1200, 43200).send.map((a) => a.kind), ['sauna_ready']);
  // later, still hot: stays active, no reminder
  const h2 = run(1000, [130, 160, 171, 172, 168]);
  const c2 = evaluate(at(h2), h2[0].ts, sauna, h2, { sauna_ready: 1120 });
  assert.ok(c2.sauna_ready);
  assert.deepEqual(diffAlerts(c2, { sauna_ready: 1120 }, 1120 + 90000, 43200), { send: [], cleared: [] });
  // below targetF but above onF and not yet armed: nothing
  assert.equal(evaluate(at(run(1000, [130, 150])), 1060, sauna, run(1000, [130, 150]), {}).sauna_ready, null);
  // cooled below onF: cleared (silently), then re-arms
  const cold = evaluate({ ts: 5000, temp_f: 100, rail_v: null }, 5000, sauna, [], { sauna_ready: 1120 });
  assert.equal(cold.sauna_ready, null);
  assert.deepEqual(diffAlerts(cold, { sauna_ready: 1120 }, 5000, 43200).cleared, ['sauna_ready']);
  assert.ok(isOneShot('sauna_ready') && !isOneShot('sauna_hot'));
});

test('sauna_hot with hysteresis', () => {
  assert.match(evaluate({ ts: 1000, temp_f: 216, rail_v: null }, 1000, sauna, []).sauna_hot, /216\.0 F.*215 F limit/);
  assert.equal(evaluate({ ts: 1000, temp_f: 214, rail_v: null }, 1000, sauna, []).sauna_hot, null);
  assert.ok(evaluate({ ts: 1000, temp_f: 214, rail_v: null }, 1000, sauna, [], { sauna_hot: 900 }).sauna_hot);
  assert.equal(evaluate({ ts: 1000, temp_f: 212, rail_v: null }, 1000, sauna, [], { sauna_hot: 900 }).sauna_hot, null);
});

test('sessionStart walks back to the first reading of the run and stops at a gap or a cool reading', () => {
  const h = run(0, [100, 125, 130, 140]);               // oldest cool, then 3 hot at 60,120,180
  assert.equal(sessionStart(h, 120, 60), 60);
  const gap = [{ ts: 1000, temp_f: 130 }, { ts: 900, temp_f: 130 }, { ts: 300, temp_f: 130 }]; // 600 s gap > 180
  assert.equal(sessionStart(gap, 120, 60), 900);
  assert.equal(sessionStart([{ ts: 1, temp_f: 90 }], 120, 60), null);
});

test('sauna_long: only after maxSessionMin of continuous heat', () => {
  const mk = (mins) => run(0, Array(mins + 1).fill(150));            // one reading per minute
  const short = mk(120), long = mk(121);
  assert.equal(evaluate(at(short), short[0].ts, sauna, short, {}).sauna_long, null);
  assert.match(evaluate(at(long), long[0].ts, sauna, long, {}).sauna_long, /121 min \(limit 120\)/);
  // a gap resets the session
  const gapped = [...long.slice(0, 10), { ts: long[10].ts - 3600, temp_f: 150 }, ...long.slice(11)].filter(Boolean);
  const g = evaluate(at(gapped), gapped[0].ts, sauna, gapped, {});
  assert.equal(g.sauna_long, null);
  // cooling clears it
  assert.equal(evaluate({ ts: 9000, temp_f: 110, rail_v: null }, 9000, sauna, long, { sauna_long: 8000 }).sauna_long, null);
});

test('sauna still reports no_checkin (with its own limit) and sensor_fault', () => {
  const stale = evaluate({ ts: 0, temp_f: 150, rail_v: null }, 41 * 60, sauna, []);
  assert.match(stale.no_checkin, /41 min \(limit 40\)/);
  assert.equal(stale.sauna_hot, null);
  assert.ok(evaluate({ ts: 0, temp_f: null, rail_v: null, batt_v: null }, 60, sauna, []).sensor_fault);
});
