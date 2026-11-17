// Pure helpers for the RV temperature Worker (no I/O, so they unit-test under plain node).

const DEVICE = /^[a-z0-9_-]{1,32}$/;

const num = (v) => (v === null || v === undefined || v === '' ? null : Number(v));
const inRange = (n, lo, hi) => n !== null && Number.isFinite(n) && n >= lo && n <= hi;

// Validate a POSTed reading. A DS18B20 reports -127 C (-196.6 F) on a fault; that is stored as a null temp.
export function parseReading(b) {
  if (!b || typeof b !== 'object') return { error: 'body must be a JSON object' };
  const device = b.device === undefined ? 'rv' : String(b.device);
  if (!DEVICE.test(device)) return { error: 'device must be 1-32 chars of a-z, 0-9, _ or -' };

  let temp_f = num(b.temp_f);
  if (temp_f !== null && (temp_f <= -196 || !inRange(temp_f, -67, 257))) temp_f = null;
  const rail_v = num(b.rail_v), batt_v = num(b.batt_v), rssi = num(b.rssi), lat = num(b.lat), lon = num(b.lon);
  if (rail_v !== null && !inRange(rail_v, 0, 40)) return { error: 'rail_v out of range' };
  if (batt_v !== null && !inRange(batt_v, 0, 6)) return { error: 'batt_v out of range' };
  if (rssi !== null && !inRange(rssi, -150, 99)) return { error: 'rssi out of range' };
  if ((lat === null) !== (lon === null)) return { error: 'send lat and lon together' };
  if (lat !== null && (!inRange(lat, -90, 90) || !inRange(lon, -180, 180))) return { error: 'lat/lon out of range' };
  if (temp_f === null && rail_v === null && batt_v === null) return { error: 'no usable measurements' };
  return { value: { device, temp_f, rail_v, batt_v, rssi: rssi === null ? null : Math.round(rssi), lat, lon } };
}

const fmtTemp = (f) => `${f.toFixed(1)} F`;

// ---- Per-device config -----------------------------------------------------------------------

const NUM_KEYS = ['lowTempF', 'highTempF', 'lowRailV', 'lowBattV', 'missedMin', 'onF', 'targetF', 'hotLimitF', 'maxSessionMin', 'activeIntervalSec'];
const SAUNA_DEFAULTS = { onF: 120, targetF: 170, hotLimitF: 215, maxSessionMin: 120, activeIntervalSec: 60 };

// Parse the DEVICES var. Malformed JSON never throws: returns { devices: {}, error }.
export function parseDevices(str) {
  if (str === undefined || str === null || str === '') return { devices: {} };
  try {
    const d = JSON.parse(str);
    if (!d || typeof d !== 'object' || Array.isArray(d)) return { devices: {}, error: 'DEVICES must be a JSON object' };
    return { devices: d };
  } catch (e) {
    return { devices: {}, error: `DEVICES is not valid JSON: ${e.message}` };
  }
}

// Global thresholds `base` + this device's overrides. Unknown device: base, label = device id.
// Bad override values are ignored (the global value stays).
export function deviceCfg(base, devices, device) {
  const d = devices && typeof devices[device] === 'object' && devices[device] ? devices[device] : {};
  const profile = d.profile === 'sauna' ? 'sauna' : 'default';
  const label = typeof d.label === 'string' && d.label.trim() ? d.label.trim().slice(0, 32) : device === 'rv' ? 'RV' : device;
  const cfg = { ...base, ...(profile === 'sauna' ? SAUNA_DEFAULTS : {}), profile, label };
  for (const k of NUM_KEYS) {
    if (d[k] !== undefined && d[k] !== null && d[k] !== '' && Number.isFinite(Number(d[k]))) cfg[k] = Number(d[k]);
  }
  return cfg;
}

// ---- Alert evaluation ------------------------------------------------------------------------

// Kinds that fire once and stay quiet: no reminder, no "Cleared" message.
const ONE_SHOT = new Set(['sauna_ready']);
export const isOneShot = (kind) => ONE_SHOT.has(kind);

export const PRIORITY = { low_temp: 5, no_checkin: 5, sauna_hot: 5, sauna_long: 4, sauna_ready: 3 };
export const priorityOf = (kind) => PRIORITY[kind] ?? 4;

// Start (unix s) of the continuous run of readings at or above onF ending at the newest row, or null.
// `history` is newest first. A gap longer than 3 x the reporting interval ends the run.
export function sessionStart(history, onF, activeIntervalSec = 60) {
  const gap = 3 * activeIntervalSec;
  let start = null, prev = null;
  for (const r of history) {
    if (r.temp_f === null || r.temp_f === undefined || r.temp_f < onF) break;
    if (prev !== null && prev - r.ts > gap) break;
    start = r.ts;
    prev = r.ts;
  }
  return start;
}

// Which alert conditions hold right now? Returns { kind: message | null }.
// `latest` newest reading row (or null), `now` unix seconds, `cfg` the device's config (see deviceCfg),
// `history` recent rows newest first (sauna profile), `active` kind -> last_sent of alerts already
// raised (lets temperature alerts use hysteresis: once on, they stay on until `hystF` past the limit).
export function evaluate(latest, now, cfg, history = [], active = {}) {
  const out = {
    no_checkin: null, low_temp: null, high_temp: null, low_rail: null, low_batt: null, sensor_fault: null,
    sauna_ready: null, sauna_long: null, sauna_hot: null,
  };
  if (!latest) return out;
  const label = cfg.label ?? 'RV';
  const hyst = cfg.hystF ?? 0;
  const on = (kind) => active[kind] !== undefined;
  const ageMin = (now - latest.ts) / 60;
  if (ageMin > cfg.missedMin) {
    out.no_checkin = `No reading for ${Math.round(ageMin)} min (limit ${cfg.missedMin}). Power, network or coverage problem?`;
    return out; // old data tells us nothing about current conditions
  }
  const t = latest.temp_f;
  if (t === null) out.sensor_fault = 'Temperature probe fault (no valid reading).';
  else if (cfg.profile === 'sauna') {
    if (t >= cfg.hotLimitF - (on('sauna_hot') ? hyst : 0)) {
      out.sauna_hot = `${label} is ${fmtTemp(t)}, at or above the ${cfg.hotLimitF} F limit.`;
    }
    if (t >= cfg.targetF || (on('sauna_ready') && t >= cfg.onF)) {
      out.sauna_ready = `${label} reached ${fmtTemp(t)} (target ${cfg.targetF} F).`;
    }
    const start = sessionStart([{ ts: latest.ts, temp_f: t }, ...history.filter((r) => r.ts < latest.ts)], cfg.onF, cfg.activeIntervalSec);
    if (start !== null && (latest.ts - start) / 60 > cfg.maxSessionMin) {
      out.sauna_long = `${label} has been above ${cfg.onF} F for ${Math.round((latest.ts - start) / 60)} min (limit ${cfg.maxSessionMin}). Still need it on?`;
    }
  } else if (t <= cfg.lowTempF + (on('low_temp') ? hyst : 0)) {
    out.low_temp = `${label} is ${fmtTemp(t)}, at or below ${cfg.lowTempF} F.`;
  } else if (t >= cfg.highTempF - (on('high_temp') ? hyst : 0)) {
    out.high_temp = `${label} is ${fmtTemp(t)}, at or above ${cfg.highTempF} F.`;
  }
  if (latest.rail_v !== null && latest.rail_v <= cfg.lowRailV) {
    out.low_rail = `External power is ${latest.rail_v.toFixed(2)} V (limit ${cfg.lowRailV} V). The outlet or charger lost power; the sensor is on its own cell.`;
  }
  // On its own cell (no external-power reading, or it reads low) and running down: warn before it dies.
  if ((latest.rail_v === null || latest.rail_v <= cfg.lowRailV) && latest.batt_v !== null && latest.batt_v <= cfg.lowBattV) {
    out.low_batt = `Running on its own battery, down to ${latest.batt_v.toFixed(2)} V (limit ${cfg.lowBattV} V). Charge or replace it soon.`;
  }
  return out;
}

// Compare current conditions with what we already told the user about.
// `active` maps kind -> last_sent (unix s). Returns notifications to send and kinds to clear.
// One-shot kinds (see isOneShot) never remind; the caller clears them without a message.
export function diffAlerts(conditions, active, now, remindSec) {
  const send = [], cleared = [];
  for (const [kind, msg] of Object.entries(conditions)) {
    const sentAt = active[kind];
    if (msg && sentAt === undefined) send.push({ kind, msg, type: 'new' });
    else if (msg && !isOneShot(kind) && now - sentAt >= remindSec) send.push({ kind, msg, type: 'reminder' });
    else if (!msg && sentAt !== undefined) cleared.push(kind);
  }
  return { send, cleared };
}

// `{label}` is replaced with the device label.
export const TITLES = {
  no_checkin: '{label} sensor offline',
  low_temp: '{label} too cold',
  high_temp: '{label} too hot',
  low_rail: '{label} power lost',
  low_batt: '{label} sensor battery low',
  sensor_fault: '{label} probe fault',
  sauna_ready: '{label} is ready',
  sauna_long: '{label} running long',
  sauna_hot: '{label} too hot',
};
export const titleOf = (kind, label = 'RV') => (TITLES[kind] ?? kind).replace('{label}', label);

// A minimal RFC 5322 plain-text message for the Email Workers send binding.
export function buildEmail({ from, to, subject, text, now = new Date(), id = crypto.randomUUID() }) {
  const domain = from.split('@')[1] || 'localhost';
  const clean = (s) => String(s).replace(/[\r\n]+/g, ' ');
  return [
    `From: RV Sensor <${clean(from)}>`,
    `To: ${clean(to)}`,
    `Subject: ${clean(subject)}`,
    `Date: ${now.toUTCString()}`,
    `Message-ID: <${id}@${domain}>`,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=utf-8',
    '',
    text,
    '',
  ].join('\r\n');
}

// Compare strings without leaking where they differ.
export function safeEqual(a, b) {
  const enc = new TextEncoder();
  const x = enc.encode(a), y = enc.encode(b);
  let diff = x.length ^ y.length;
  const n = Math.max(x.length, y.length);
  for (let i = 0; i < n; i++) diff |= (x[i] ?? 0) ^ (y[i] ?? 0);
  return diff === 0;
}
