// E-ink gift frame API: Cloudflare Worker + D1.
//
//   Frame  (header X-Token):      GET /api/eink/frame  -> weather + poem/message + seconds to sleep
//   Admin  (header X-Admin-Key):  /api/eink/devices[/:id[/messages|/preview]], /api/eink/messages/:id,
//                                 /api/eink/geocode?q=
//   Page:                         GET /api/eink/admin  (HTML; the key is typed in, never stored server-side)

import {
  latin1Safe, localParts, validTz, parseSlots, planWake, parseWeather, weatherUrl,
  hash, linecountFor, cleanPoem, pickBody, buildFrame, DATE,
} from './frame.js';
import { FALLBACK_POEMS } from './poems.js';
import { ADMIN_HTML } from './admin.js';

const TOMORROW_FROM_MIN = 15 * 60;
const DEFAULT_SLOTS = '06:00,17:00';

export function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });
}
const err = (status, message) => json({ error: message }, status);

export function newToken() {
  // 20 url-safe characters: short enough to type into the frame's setup page if ever needed.
  const abc = 'abcdefghijkmnpqrstuvwxyz23456789';
  const bytes = crypto.getRandomValues(new Uint8Array(20));
  return [...bytes].map((b) => abc[b % abc.length]).join('');
}

export function safeEqual(a, b) {
  const enc = new TextEncoder();
  const x = enc.encode(a), y = enc.encode(b);
  let diff = x.length ^ y.length;
  for (let i = 0; i < Math.max(x.length, y.length); i++) diff |= (x[i] ?? 0) ^ (y[i] ?? 0);
  return diff === 0;
}

// Validate a device body. partial=true for PATCH. Returns { value } or { error }.
export function parseDevice(b, partial = false) {
  if (!b || typeof b !== 'object') return { error: 'body must be a JSON object' };
  const v = {};
  const has = (k) => b[k] !== undefined;
  if (has('name') || !partial) {
    const s = typeof b.name === 'string' ? b.name.trim().replace(/\s+/g, ' ') : '';
    if (!s || s.length > 40) return { error: 'name is required (1-40 characters)' };
    v.name = s;
  }
  if (has('place')) {
    const s = typeof b.place === 'string' ? latin1Safe(b.place).trim() : '';
    if (s.length > 30) return { error: 'place must be 30 characters or fewer' };
    v.place = s;
  }
  for (const [k, lim] of [['lat', 90], ['lon', 180]]) {
    if (has(k) || !partial) {
      const n = Number(b[k]);
      if (b[k] === null || b[k] === '' || !Number.isFinite(n) || Math.abs(n) > lim) return { error: `${k} must be a number within +/-${lim}` };
      v[k] = Math.round(n * 1e4) / 1e4;
    }
  }
  if (has('tz') || !partial) {
    if (!validTz(b.tz)) return { error: 'tz must be an IANA time zone like America/New_York' };
    v.tz = b.tz;
  }
  if (has('units')) {
    if (b.units !== 'F' && b.units !== 'C') return { error: 'units must be "F" or "C"' };
    v.units = b.units;
  }
  if (has('refresh')) {
    const slots = parseSlots(b.refresh);
    if (!slots) return { error: 'refresh must be HH:MM times separated by commas, e.g. 06:00,17:00' };
    v.refresh = slots.map((m) => `${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`).join(',');
  }
  return { value: v };
}

export function parseMessage(b) {
  if (!b || typeof b !== 'object') return { error: 'body must be a JSON object' };
  const body = typeof b.body === 'string' ? b.body.trim() : '';
  if (!body || body.length > 400) return { error: 'body is required (1-400 characters)' };
  const from = typeof b.from === 'string' ? b.from.trim() : '';
  if (from.length > 40) return { error: 'from must be 40 characters or fewer' };
  const showOn = b.show_on === undefined || b.show_on === null || b.show_on === '' ? null : b.show_on;
  if (showOn !== null && (!DATE.test(showOn) || isNaN(Date.parse(showOn + 'T12:00:00Z')))) return { error: 'show_on must be YYYY-MM-DD or empty' };
  const pinned = Boolean(b.pinned) && showOn === null;
  return { value: { body, from_name: from || null, show_on: showOn, pinned: pinned ? 1 : 0 } };
}

// Telemetry headers from the frame; anything malformed is ignored.
export function parseTelemetry(h) {
  const int = (v, lo, hi) => { const n = Number.parseInt(v ?? '', 10); return Number.isFinite(n) && n >= lo && n <= hi ? n : null; };
  const fw = h.get('x-fw');
  return {
    battery_mv: int(h.get('x-battery-mv'), 2000, 5500),
    rssi: int(h.get('x-rssi'), -127, 0),
    fw: fw && /^[\w.+-]{1,24}$/.test(fw) ? fw : null,
  };
}

async function poemOfTheDay(env, date) {
  const row = await env.DB.prepare('SELECT poem FROM daily_poems WHERE date = ?1').bind(date).first();
  if (row) return JSON.parse(row.poem);
  let poem = null;
  for (let attempt = 0; attempt < 4 && !poem; attempt++) {
    try {
      const r = await fetch(`https://poetrydb.org/random,linecount/1;${linecountFor(date, attempt)}`,
        { signal: AbortSignal.timeout(4000) });
      if (r.ok) { const j = await r.json(); poem = Array.isArray(j) ? cleanPoem(j[0]) : null; }
    } catch { /* try again, then fall back */ }
  }
  poem = poem || cleanPoem(FALLBACK_POEMS[hash(date) % FALLBACK_POEMS.length]);
  await env.DB.prepare('INSERT OR IGNORE INTO daily_poems (date, poem) VALUES (?1, ?2)').bind(date, JSON.stringify(poem)).run();
  const winner = await env.DB.prepare('SELECT poem FROM daily_poems WHERE date = ?1').bind(date).first();
  return winner ? JSON.parse(winner.poem) : poem;
}

async function weatherFor(device, tomorrow) {
  try {
    const r = await fetch(weatherUrl(device), { cf: { cacheTtl: 900, cacheEverything: true }, signal: AbortSignal.timeout(5000) });
    return r.ok ? parseWeather(await r.json(), tomorrow, device.units) : null;
  } catch { return null; }
}

export async function frameFor(env, device, now = new Date()) {
  const local = localParts(now, device.tz);
  const plan = planWake(local.minutes, parseSlots(device.refresh) || parseSlots(DEFAULT_SLOTS));
  const { results: messages } = await env.DB.prepare(
    'SELECT body, from_name, show_on, pinned, created_at FROM messages WHERE device_id = ?1 AND (show_on = ?2 OR (pinned = 1 AND show_on IS NULL))',
  ).bind(device.id, local.date).all();
  const [weather, poem] = await Promise.all([
    weatherFor(device, plan.effectiveMin >= TOMORROW_FROM_MIN),
    messages.length ? null : poemOfTheDay(env, local.date),
  ]);
  return buildFrame({ device, weather, body: pickBody(messages, local.date, poem), sleepS: plan.sleepS, local });
}

const readJson = async (req) => { try { return await req.json(); } catch { return null; } };
const isAdmin = (req, env) => {
  const key = req.headers.get('x-admin-key');
  return Boolean(env.ADMIN_KEY) && Boolean(key) && safeEqual(key, env.ADMIN_KEY);
};
const DEVICE_COLS = 'id, name, token, place, lat, lon, tz, units, refresh, last_seen, battery_mv, rssi, fw, created_at';

async function handle(request, env) {
  const url = new URL(request.url);
  const path = url.pathname.replace(/^\/api\/eink/, '') || '/';
  const method = request.method;

  if (path === '/frame' && method === 'GET') {
    const token = request.headers.get('x-token') || url.searchParams.get('t') || '';
    if (!token || token.length > 64) return err(401, 'unknown frame');
    const device = await env.DB.prepare(`SELECT ${DEVICE_COLS} FROM devices WHERE token = ?1`).bind(token).first();
    if (!device) return err(401, 'unknown frame');
    const t = parseTelemetry(request.headers);
    await env.DB.prepare(
      "UPDATE devices SET last_seen = datetime('now'), battery_mv = COALESCE(?2, battery_mv), rssi = COALESCE(?3, rssi), fw = COALESCE(?4, fw) WHERE id = ?1",
    ).bind(device.id, t.battery_mv, t.rssi, t.fw).run();
    return json(await frameFor(env, device));
  }

  if (path === '/admin' && method === 'GET') {
    return new Response(ADMIN_HTML, {
      headers: {
        'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store',
        'content-security-policy': "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; form-action 'none'",
        'x-frame-options': 'DENY', 'referrer-policy': 'no-referrer',
      },
    });
  }

  if (!isAdmin(request, env)) return err(401, 'admin key required');

  if (path === '/geocode' && method === 'GET') {
    const q = (url.searchParams.get('q') || '').trim();
    if (!q || q.length > 80) return err(400, 'q is required');
    const r = await fetch(`https://geocoding-api.open-meteo.com/v1/search?${new URLSearchParams({ name: q, count: '5', format: 'json' })}`,
      { signal: AbortSignal.timeout(5000) });
    const j = r.ok ? await r.json() : {};
    return json((j.results || []).map((p) => ({
      label: [p.name, p.admin1, p.country_code].filter(Boolean).join(', '), place: p.name,
      lat: p.latitude, lon: p.longitude, tz: p.timezone,
    })));
  }

  if (path === '/devices' && method === 'GET') {
    const { results } = await env.DB.prepare(`SELECT ${DEVICE_COLS} FROM devices ORDER BY id`).all();
    return json(results);
  }
  if (path === '/devices' && method === 'POST') {
    const p = parseDevice(await readJson(request));
    if (p.error) return err(400, p.error);
    const d = { place: '', units: 'F', refresh: DEFAULT_SLOTS, ...p.value };
    const row = await env.DB.prepare(
      `INSERT INTO devices (name, token, place, lat, lon, tz, units, refresh) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8) RETURNING ${DEVICE_COLS}`,
    ).bind(d.name, newToken(), d.place, d.lat, d.lon, d.tz, d.units, d.refresh).first();
    return json(row, 201);
  }

  let m = path.match(/^\/devices\/(\d+)(\/messages|\/preview)?$/);
  if (m) {
    const id = Number(m[1]);
    const device = await env.DB.prepare(`SELECT ${DEVICE_COLS} FROM devices WHERE id = ?1`).bind(id).first();
    if (!device) return err(404, 'no such device');
    if (!m[2] && method === 'PATCH') {
      const p = parseDevice(await readJson(request), true);
      if (p.error) return err(400, p.error);
      const keys = Object.keys(p.value);
      if (!keys.length) return json(device);
      const row = await env.DB.prepare(
        `UPDATE devices SET ${keys.map((k, i) => `${k} = ?${i + 2}`).join(', ')} WHERE id = ?1 RETURNING ${DEVICE_COLS}`,
      ).bind(id, ...keys.map((k) => p.value[k])).first();
      return json(row);
    }
    if (!m[2] && method === 'DELETE') {
      await env.DB.batch([
        env.DB.prepare('DELETE FROM messages WHERE device_id = ?1').bind(id),
        env.DB.prepare('DELETE FROM devices WHERE id = ?1').bind(id),
      ]);
      return json({ ok: true });
    }
    if (m[2] === '/preview' && method === 'GET') return json(await frameFor(env, device));
    if (m[2] === '/messages' && method === 'GET') {
      const { results } = await env.DB.prepare(
        'SELECT id, body, from_name, show_on, pinned, created_at FROM messages WHERE device_id = ?1 ORDER BY COALESCE(show_on, created_at) DESC',
      ).bind(id).all();
      return json(results);
    }
    if (m[2] === '/messages' && method === 'POST') {
      const p = parseMessage(await readJson(request));
      if (p.error) return err(400, p.error);
      const v = p.value;
      const row = await env.DB.prepare(
        'INSERT INTO messages (device_id, body, from_name, show_on, pinned) VALUES (?1, ?2, ?3, ?4, ?5) RETURNING id, body, from_name, show_on, pinned, created_at',
      ).bind(id, v.body, v.from_name, v.show_on, v.pinned).first();
      return json(row, 201);
    }
  }

  m = path.match(/^\/messages\/(\d+)$/);
  if (m && method === 'DELETE') {
    await env.DB.prepare('DELETE FROM messages WHERE id = ?1').bind(Number(m[1])).run();
    return json({ ok: true });
  }

  return err(404, 'not found');
}

export default {
  async fetch(request, env) {
    try {
      return await handle(request, env);
    } catch (e) {
      console.error('eink error', e && e.message);
      return err(500, 'server error');
    }
  },
};
