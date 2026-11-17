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

// Which alert conditions hold right now? Returns { kind: message | null }.
// `latest` is the newest reading row (or null), `now` unix seconds, `cfg` numeric thresholds.
export function evaluate(latest, now, cfg) {
  const out = { no_checkin: null, low_temp: null, high_temp: null, low_rail: null, low_batt: null, sensor_fault: null };
  if (!latest) return out;
  const ageMin = (now - latest.ts) / 60;
  if (ageMin > cfg.missedMin) {
    out.no_checkin = `No reading for ${Math.round(ageMin)} min (limit ${cfg.missedMin}). Power, modem or coverage problem?`;
    return out; // old data tells us nothing about current conditions
  }
  if (latest.temp_f === null) out.sensor_fault = 'Temperature probe fault (no valid reading).';
  else if (latest.temp_f <= cfg.lowTempF) out.low_temp = `RV is ${fmtTemp(latest.temp_f)}, at or below ${cfg.lowTempF} F.`;
  else if (latest.temp_f >= cfg.highTempF) out.high_temp = `RV is ${fmtTemp(latest.temp_f)}, at or above ${cfg.highTempF} F.`;
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
// `active` maps kind -> last_sent (unix s). Returns notifications to send and kinds to clear/touch.
export function diffAlerts(conditions, active, now, remindSec) {
  const send = [], cleared = [];
  for (const [kind, msg] of Object.entries(conditions)) {
    const sentAt = active[kind];
    if (msg && sentAt === undefined) send.push({ kind, msg, type: 'new' });
    else if (msg && now - sentAt >= remindSec) send.push({ kind, msg, type: 'reminder' });
    else if (!msg && sentAt !== undefined) cleared.push(kind);
  }
  return { send, cleared };
}

export const TITLES = {
  no_checkin: 'RV sensor offline',
  low_temp: 'RV too cold',
  high_temp: 'RV too hot',
  low_rail: 'RV power lost',
  low_batt: 'RV sensor battery low',
  sensor_fault: 'RV probe fault',
};

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
