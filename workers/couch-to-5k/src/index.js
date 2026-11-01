// Couch to Turkey Trot API: Cloudflare Worker + D1.
//
//   Admin (header X-Admin-Key):   POST/GET /api/c25k/people, DELETE /api/c25k/people/:id
//   Person (header X-Token):      GET /api/c25k/me, PATCH /api/c25k/me,
//                                 PUT/DELETE /api/c25k/entries/:planId
//
// The edit token can read and write; the view token can only read.

const LEVELS = ['beginner', 'intermediate', 'runner'];
const PLAN_ID = /^(s(0[1-9]|1[01])|race)$/;
const DATE = /^\d{4}-\d{2}-\d{2}$/;
const COLOR = /^#[0-9a-f]{6}$/;
// Default dot colors, handed out by person id until someone picks their own.
export const PALETTE = ['#d9591f', '#2f7fb8', '#3f9e5b', '#b04fb4', '#e0a31b', '#d6456b', '#2fa7a0', '#7a5cc8', '#8a6a3b', '#5b6b7a'];
const PROD_ORIGIN = 'https://www.extra-ransom.net';
const LOCAL_ORIGIN = /^http:\/\/(localhost|127\.0\.0\.1):\d+$/; // local development against `wrangler dev`

export function json(body, status = 200, extra = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...extra },
  });
}
const err = (status, message) => json({ error: message }, status);

export function newToken() {
  const bytes = crypto.getRandomValues(new Uint8Array(24));
  let s = '';
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
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

// Body for PUT /days/:date. Returns { value } or { error }.
export function parseDay(date, b) {
  if (!DATE.test(date) || isNaN(Date.parse(date + 'T12:00:00Z'))) return { error: 'date must be YYYY-MM-DD' };
  if (date < '2026-10-01' || date > '2026-12-31') return { error: 'date is outside the plan period' };
  if (!b || typeof b !== 'object' || typeof b.strength !== 'boolean' || typeof b.sauna !== 'boolean') {
    return { error: 'send {"strength": true/false, "sauna": true/false, "bike": null, "indoor" or "outdoor"}' };
  }
  const bike = b.bike === undefined ? null : b.bike;
  if (bike !== null && bike !== 'indoor' && bike !== 'outdoor') return { error: 'bike must be null, "indoor" or "outdoor"' };
  return { value: { strength: b.strength, sauna: b.sauna, bike } };
}

export function cleanColor(v) {
  if (typeof v !== 'string') return null;
  const s = v.trim().toLowerCase();
  return COLOR.test(s) ? s : null;
}
export function colorOf(row) { return row.color || PALETTE[(row.id - 1) % PALETTE.length]; }

export function cleanName(v) {
  if (typeof v !== 'string') return null;
  const s = v.trim().replace(/\s+/g, ' ');
  return s.length >= 1 && s.length <= 40 ? s : null;
}

// Returns { value } or { error }. Every field is optional except date.
export function parseEntry(b) {
  if (!b || typeof b !== 'object') return { error: 'body must be a JSON object' };
  if (typeof b.date !== 'string' || !DATE.test(b.date) || isNaN(Date.parse(b.date + 'T12:00:00Z'))) {
    return { error: 'date must be YYYY-MM-DD' };
  }
  const num = (v, min, max, name) => {
    if (v === null || v === undefined || v === '') return { v: null };
    const n = Number(v);
    if (!Number.isFinite(n) || n < min || n > max) return { error: `${name} must be between ${min} and ${max}` };
    return { v: n };
  };
  const dist = num(b.distance_mi, 0, 50, 'distance_mi');
  if (dist.error) return dist;
  const dur = num(b.duration_min, 0, 600, 'duration_min');
  if (dur.error) return dur;
  const pct = num(b.run_pct, 0, 100, 'run_pct');
  if (pct.error) return pct;
  let note = b.note;
  if (note === undefined || note === null) note = null;
  else if (typeof note !== 'string' || note.length > 1000) return { error: 'note must be text up to 1000 characters' };
  else note = note.trim() || null;
  return {
    value: {
      date: b.date,
      distance_mi: dist.v,
      duration_min: dur.v,
      run_pct: pct.v === null ? null : Math.round(pct.v),
      note,
    },
  };
}

function corsHeaders(request) {
  const origin = request.headers.get('origin');
  if (!origin || (origin !== PROD_ORIGIN && !LOCAL_ORIGIN.test(origin))) return {};
  return {
    'access-control-allow-origin': origin,
    'access-control-allow-headers': 'content-type, x-token, x-admin-key',
    'access-control-allow-methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
    vary: 'Origin',
  };
}

async function readJson(request) {
  try { return await request.json(); } catch { return null; }
}

function isAdmin(request, env) {
  const key = request.headers.get('x-admin-key');
  return Boolean(env.ADMIN_KEY) && Boolean(key) && safeEqual(key, env.ADMIN_KEY);
}

async function personByToken(env, token) {
  if (!token || token.length > 64) return null;
  const row = await env.DB
    .prepare('SELECT id, name, level, color, edit_token, view_token FROM people WHERE edit_token = ?1 OR view_token = ?1')
    .bind(token).first();
  if (!row) return null;
  return { ...row, canEdit: safeEqual(row.edit_token, token) };
}

async function handle(request, env) {
  const url = new URL(request.url);
  const path = url.pathname.replace(/^\/api\/c25k/, '') || '/';
  const method = request.method;

  // ---- public team view: colored dots only, no names, ids, tokens or notes ----
  if (path === '/team' && method === 'GET') {
    const { results } = await env.DB.prepare(
      `SELECT p.id, p.level, p.color, e.plan_id, e.distance_mi, e.duration_min, e.run_pct
         FROM people p LEFT JOIN entries e ON e.person_id = p.id ORDER BY p.id, e.date`).all();
    const byId = new Map();
    for (const r of results) {
      let t = byId.get(r.id);
      if (!t) { t = { color: colorOf(r), level: r.level, sessions: [], distance_mi: 0, duration_min: 0, pcts: [] }; byId.set(r.id, t); }
      if (r.plan_id) {
        t.sessions.push(r.plan_id);
        if (r.distance_mi != null) t.distance_mi += r.distance_mi;
        if (r.duration_min != null) t.duration_min += r.duration_min;
        if (r.run_pct != null) t.pcts.push(r.run_pct);
      }
    }
    const people = [...byId.values()].map((t) => ({
      color: t.color, level: t.level, sessions: t.sessions,
      distance_mi: Math.round(t.distance_mi * 100) / 100,
      duration_min: Math.round(t.duration_min * 10) / 10,
      run_pct: t.pcts.length ? Math.round(t.pcts.reduce((a, b) => a + b, 0) / t.pcts.length) : null,
    }));
    return json({ people }, 200, { 'cache-control': 'public, max-age=30' });
  }

  // ---- admin ----
  if (path === '/people' || /^\/people\/\d+$/.test(path)) {
    if (!isAdmin(request, env)) return err(401, 'admin key required');
    if (path === '/people' && method === 'GET') {
      const { results } = await env.DB.prepare(
        `SELECT p.id, p.name, p.level, p.color, p.edit_token, p.view_token, p.created_at,
                (SELECT COUNT(*) FROM entries e WHERE e.person_id = p.id) AS entries
           FROM people p ORDER BY p.id`).all();
      return json({ people: results.map((r) => ({ ...r, color: colorOf(r) })) });
    }
    if (path === '/people' && method === 'POST') {
      const b = await readJson(request);
      const name = cleanName(b && b.name);
      if (!name) return err(400, 'name is required (1-40 characters)');
      const level = b.level === undefined ? 'beginner' : b.level;
      if (!LEVELS.includes(level)) return err(400, 'level must be one of ' + LEVELS.join(', '));
      const color = b.color === undefined ? null : cleanColor(b.color);
      if (b.color !== undefined && !color) return err(400, 'color must look like #d9591f');
      const edit = newToken(), view = newToken();
      const r = await env.DB.prepare('INSERT INTO people (name, level, color, edit_token, view_token) VALUES (?1, ?2, ?3, ?4, ?5)')
        .bind(name, level, color, edit, view).run();
      const id = r.meta.last_row_id;
      return json({ id, name, level, color: colorOf({ id, color }), edit_token: edit, view_token: view }, 201);
    }
    if (method === 'DELETE') {
      const id = Number(path.split('/')[2]);
      await env.DB.prepare('DELETE FROM entries WHERE person_id = ?1').bind(id).run();
      await env.DB.prepare('DELETE FROM days WHERE person_id = ?1').bind(id).run();
      const r = await env.DB.prepare('DELETE FROM people WHERE id = ?1').bind(id).run();
      return r.meta.changes ? json({ ok: true }) : err(404, 'no such person');
    }
    return err(405, 'method not allowed');
  }

  // ---- a person, by token ----
  const person = await personByToken(env, request.headers.get('x-token'));
  if (path === '/me' || /^\/entries\/[a-z0-9]+$/.test(path) || /^\/days\/[\d-]+$/.test(path)) {
    if (!person) return err(401, 'unknown link');
  }

  if (path === '/me' && method === 'GET') {
    const { results } = await env.DB.prepare(
      'SELECT plan_id, date, distance_mi, duration_min, run_pct, note, updated_at FROM entries WHERE person_id = ?1 ORDER BY date, plan_id')
      .bind(person.id).all();
    const { results: dayRows } = await env.DB.prepare(
      'SELECT date, strength, sauna, bike FROM days WHERE person_id = ?1 ORDER BY date').bind(person.id).all();
    return json({
      person: { name: person.name, level: person.level, color: colorOf(person), can_edit: person.canEdit },
      entries: results,
      days: dayRows.map((d) => ({ date: d.date, strength: !!d.strength, sauna: !!d.sauna, bike: d.bike || null })),
    });
  }

  if (path === '/me' && method === 'PATCH') {
    if (!person.canEdit) return err(403, 'this link is read-only');
    const b = await readJson(request);
    if (!b || typeof b !== 'object' || (b.level === undefined && b.color === undefined)) return err(400, 'send a level and/or a color');
    if (b.level !== undefined && !LEVELS.includes(b.level)) return err(400, 'level must be one of ' + LEVELS.join(', '));
    const color = b.color === undefined ? undefined : cleanColor(b.color);
    if (b.color !== undefined && !color) return err(400, 'color must look like #d9591f');
    const level = b.level === undefined ? person.level : b.level;
    const chosen = color === undefined ? person.color : color;
    await env.DB.prepare('UPDATE people SET level = ?1, color = ?2 WHERE id = ?3').bind(level, chosen, person.id).run();
    return json({ ok: true, level, color: colorOf({ id: person.id, color: chosen }) });
  }

  const dm = path.match(/^\/days\/([\d-]+)$/);
  if (dm) {
    if (!person.canEdit) return err(403, 'this link is read-only');
    if (method !== 'PUT') return err(405, 'method not allowed');
    const parsed = parseDay(dm[1], await readJson(request));
    if (parsed.error) return err(400, parsed.error);
    const { strength, sauna, bike } = parsed.value;
    if (!strength && !sauna && !bike) {
      await env.DB.prepare('DELETE FROM days WHERE person_id = ?1 AND date = ?2').bind(person.id, dm[1]).run();
    } else {
      await env.DB.prepare(
        `INSERT INTO days (person_id, date, strength, sauna, bike) VALUES (?1, ?2, ?3, ?4, ?5)
         ON CONFLICT (person_id, date) DO UPDATE SET strength = excluded.strength, sauna = excluded.sauna, bike = excluded.bike, updated_at = datetime('now')`)
        .bind(person.id, dm[1], strength ? 1 : 0, sauna ? 1 : 0, bike).run();
    }
    return json({ ok: true, date: dm[1], strength, sauna, bike });
  }

  const m = path.match(/^\/entries\/([a-z0-9]+)$/);
  if (m) {
    const planId = m[1];
    if (!PLAN_ID.test(planId)) return err(400, 'unknown session');
    if (!person.canEdit) return err(403, 'this link is read-only');
    if (method === 'PUT') {
      const parsed = parseEntry(await readJson(request));
      if (parsed.error) return err(400, parsed.error);
      const e = parsed.value;
      await env.DB.prepare(
        `INSERT INTO entries (person_id, plan_id, date, distance_mi, duration_min, run_pct, note)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)
         ON CONFLICT (person_id, plan_id) DO UPDATE SET
           date = excluded.date, distance_mi = excluded.distance_mi, duration_min = excluded.duration_min,
           run_pct = excluded.run_pct, note = excluded.note, updated_at = datetime('now')`)
        .bind(person.id, planId, e.date, e.distance_mi, e.duration_min, e.run_pct, e.note).run();
      return json({ ok: true, plan_id: planId, ...e });
    }
    if (method === 'DELETE') {
      await env.DB.prepare('DELETE FROM entries WHERE person_id = ?1 AND plan_id = ?2').bind(person.id, planId).run();
      return json({ ok: true });
    }
    return err(405, 'method not allowed');
  }

  return err(404, 'not found');
}

export default {
  async fetch(request, env) {
    const cors = corsHeaders(request);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    let res;
    try {
      res = await handle(request, env);
    } catch (e) {
      console.error('c25k error', e && e.message);
      res = err(500, 'server error');
    }
    const out = new Response(res.body, res);
    for (const [k, v] of Object.entries(cors)) out.headers.set(k, v);
    return out;
  },
};
