// Pure helpers for the frame payload: no D1, no fetch. Unit-tested in test/frame.test.js.

export const SLOT = /^([01]\d|2[0-3]):([0-5]\d)$/;
export const DATE = /^\d{4}-\d{2}-\d{2}$/;
const GRACE_MIN = 25;            // a wake this early for a slot counts as that slot (RTC drift)
const MIN_SLEEP_S = 10 * 60;
const MAX_SLEEP_S = 16 * 3600;
const TOMORROW_FROM_MIN = 15 * 60;   // after 3 pm the header shows tomorrow's forecast

// The frame's fonts are Latin-1 only. Map common typography to ASCII and drop the rest.
export function latin1Safe(s) {
  if (typeof s !== 'string') return '';
  let out = s
    .replace(/[‘’‚‛′]/g, "'")
    .replace(/[“”„‟″]/g, '"')
    .replace(/\s*[—―]\s*/g, ' - ')
    .replace(/[‐-–−]/g, '-')
    .replace(/…/g, '...')
    .replace(/[  -   　]/g, ' ')
    .replace(/[​-‍﻿]/g, '');
  // Anything else above Latin-1: try its accent-stripped form (e.g. "ł" stays dropped, "ő" -> "o").
  out = [...out.normalize('NFC')].map((c) => {
    if (c.codePointAt(0) <= 255) return c;
    const base = c.normalize('NFKD').replace(/[\u0300-\u036f]/g, '');
    return [...base].every((b) => b.codePointAt(0) <= 255) ? base : '';
  }).join('');
  return [...out].filter((c) => c.codePointAt(0) <= 255 && (c >= ' ' || c === '\n')).join('');
}

// { date: 'YYYY-MM-DD', minutes, dateLabel: 'Sunday, November 22', timeLabel: '6:02 AM' }
export function localParts(now, tz) {
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-US', {
    timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hourCycle: 'h23',
  }).formatToParts(now).map((x) => [x.type, x.value]));
  const dateLabel = new Intl.DateTimeFormat('en-US', { timeZone: tz, weekday: 'long', month: 'long', day: 'numeric' }).format(now);
  const timeLabel = new Intl.DateTimeFormat('en-US', { timeZone: tz, weekday: 'short', hour: 'numeric', minute: '2-digit' }).format(now);
  return {
    date: `${p.year}-${p.month}-${p.day}`,
    minutes: Number(p.hour) * 60 + Number(p.minute),
    dateLabel: latin1Safe(dateLabel),
    timeLabel: latin1Safe(timeLabel).replace(',', ''),
  };
}

export function validTz(tz) {
  if (typeof tz !== 'string' || !tz || tz.length > 64) return false;
  try { new Intl.DateTimeFormat('en-US', { timeZone: tz }); return true; } catch { return false; }
}

// "06:00,17:00" -> [360, 1020]; null if invalid.
export function parseSlots(s) {
  if (typeof s !== 'string') return null;
  const parts = s.split(',').map((x) => x.trim()).filter(Boolean);
  if (!parts.length || parts.length > 8 || !parts.every((x) => SLOT.test(x))) return null;
  const mins = [...new Set(parts.map((x) => Number(x.slice(0, 2)) * 60 + Number(x.slice(3))))].sort((a, b) => a - b);
  return mins;
}

// When does the frame wake next, and which slot is this wake for?
export function planWake(nowMin, slots) {
  const all = [...slots.map((m) => m - 1440), ...slots, ...slots.map((m) => m + 1440)];
  const current = Math.max(...all.filter((m) => m <= nowMin + GRACE_MIN));
  const next = Math.min(...all.filter((m) => m > nowMin + GRACE_MIN));
  const sleepS = Math.min(MAX_SLEEP_S, Math.max(MIN_SLEEP_S, (next - nowMin) * 60));
  // An early wake (within the grace window) is treated as happening at its slot.
  const effectiveMin = current > nowMin ? current : nowMin;
  return { sleepS, effectiveMin: ((effectiveMin % 1440) + 1440) % 1440 };
}

const WMO = [
  [[0], 'clear', 'Clear'], [[1], 'clear', 'Mostly clear'], [[2], 'partly', 'Partly cloudy'], [[3], 'cloudy', 'Cloudy'],
  [[45, 48], 'fog', 'Fog'],
  [[51, 53, 55, 56, 57], 'drizzle', 'Drizzle'],
  [[61, 63, 66, 80, 81], 'rain', 'Rain'], [[65, 67, 82], 'rain', 'Heavy rain'],
  [[71, 73, 77, 85], 'snow', 'Snow'], [[75, 86], 'snow', 'Heavy snow'],
  [[95, 96, 99], 'storm', 'Thunderstorms'],
];
export function wmo(code) {
  for (const [codes, icon, text] of WMO) if (codes.includes(code)) return { icon, text };
  return { icon: 'cloudy', text: '' };
}

// Open-Meteo forecast JSON -> header line. Index 0 = today, 1 = tomorrow.
export function parseWeather(om, tomorrow, unit) {
  const d = om && om.daily;
  const i = tomorrow ? 1 : 0;
  if (!d || !Array.isArray(d.temperature_2m_max) || d.temperature_2m_max[i] == null) return null;
  const { icon, text } = wmo(d.weather_code?.[i]);
  return {
    label: tomorrow ? 'Tomorrow' : 'Today',
    icon, text,
    hi: Math.round(d.temperature_2m_max[i]),
    lo: Math.round(d.temperature_2m_min[i]),
    unit,
    pop: d.precipitation_probability_max?.[i] ?? null,
  };
}

export function weatherUrl(device) {
  const q = new URLSearchParams({
    latitude: String(device.lat), longitude: String(device.lon),
    daily: 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max',
    timezone: device.tz, forecast_days: '2',
  });
  if (device.units === 'F') q.set('temperature_unit', 'fahrenheit');
  return `https://api.open-meteo.com/v1/forecast?${q}`;
}

// Small, stable string hash (FNV-1a) for picking the day's line count.
export function hash(s) {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
  return h;
}
export function linecountFor(date, attempt) { return 4 + ((hash(date) + attempt * 7) % 11); }   // 4..14

// What fits the screen: <=16 lines, <=70 chars per line, <=650 chars in all.
export function cleanPoem(p) {
  if (!p || typeof p.title !== 'string' || typeof p.author !== 'string' || !Array.isArray(p.lines)) return null;
  const lines = p.lines.map((l) => latin1Safe(String(l)).trimEnd());
  while (lines.length && !lines[lines.length - 1].trim()) lines.pop();
  const text = lines.filter((l) => l.trim());
  if (!text.length || lines.length > 16) return null;
  if (text.some((l) => l.length > 70) || lines.join('').length > 650) return null;
  const title = latin1Safe(p.title).trim();
  if (!title || title.length > 80) return null;
  return { title, author: latin1Safe(p.author).trim(), lines };
}

// Dated message for today > newest pinned message > poem of the day.
export function pickBody(messages, today, poem) {
  const newest = (a, b) => (a.created_at < b.created_at ? 1 : -1);
  const dated = messages.filter((m) => m.show_on === today).sort(newest)[0];
  const pinned = messages.filter((m) => m.pinned && !m.show_on).sort(newest)[0];
  const m = dated || pinned;
  if (m) return { kind: 'message', text: latin1Safe(m.body).trim(), from: latin1Safe(m.from_name || '').trim() };
  return { kind: 'poem', ...poem };
}

export function buildFrame({ device, weather, body, sleepS, local }) {
  return {
    v: 1,
    date: local.dateLabel,
    place: latin1Safe(device.place || ''),
    updated: local.timeLabel,
    weather,
    body,
    sleep_s: sleepS,
  };
}
