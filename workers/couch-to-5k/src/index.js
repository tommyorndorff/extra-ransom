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
    .prepare('SELECT id, name, level, edit_token, view_token FROM people WHERE edit_token = ?1 OR view_token = ?1')
    .bind(token).first();
  if (!row) return null;
  return { ...row, canEdit: safeEqual(row.edit_token, token) };
}

async function handle(request, env) {
  const url = new URL(request.url);
  const path = url.pathname.replace(/^\/api\/c25k/, '') || '/';
  const method = request.method;

  // ---- admin ----
  if (path === '/people' || /^\/people\/\d+$/.test(path)) {
    if (!isAdmin(request, env)) return err(401, 'admin key required');
    if (path === '/people' && method === 'GET') {
      const { results } = await env.DB.prepare(
        `SELECT p.id, p.name, p.level, p.edit_token, p.view_token, p.created_at,
                (SELECT COUNT(*) FROM entries e WHERE e.person_id = p.id) AS entries
           FROM people p ORDER BY p.id`).all();
      return json({ people: results });
    }
    if (path === '/people' && method === 'POST') {
      const b = await readJson(request);
      const name = cleanName(b && b.name);
      if (!name) return err(400, 'name is required (1-40 characters)');
      const level = b.level === undefined ? 'beginner' : b.level;
      if (!LEVELS.includes(level)) return err(400, 'level must be one of ' + LEVELS.join(', '));
      const edit = newToken(), view = newToken();
      const r = await env.DB.prepare('INSERT INTO people (name, level, edit_token, view_token) VALUES (?1, ?2, ?3, ?4)')
        .bind(name, level, edit, view).run();
      return json({ id: r.meta.last_row_id, name, level, edit_token: edit, view_token: view }, 201);
    }
    if (method === 'DELETE') {
      const id = Number(path.split('/')[2]);
      await env.DB.prepare('DELETE FROM entries WHERE person_id = ?1').bind(id).run();
      const r = await env.DB.prepare('DELETE FROM people WHERE id = ?1').bind(id).run();
      return r.meta.changes ? json({ ok: true }) : err(404, 'no such person');
    }
    return err(405, 'method not allowed');
  }

  // ---- a person, by token ----
  const person = await personByToken(env, request.headers.get('x-token'));
  if (path === '/me' || /^\/entries\/[a-z0-9]+$/.test(path)) {
    if (!person) return err(401, 'unknown link');
  }

  if (path === '/me' && method === 'GET') {
    const { results } = await env.DB.prepare(
      'SELECT plan_id, date, distance_mi, duration_min, run_pct, note, updated_at FROM entries WHERE person_id = ?1 ORDER BY date, plan_id')
      .bind(person.id).all();
    return json({
      person: { name: person.name, level: person.level, can_edit: person.canEdit },
      entries: results,
    });
  }

  if (path === '/me' && method === 'PATCH') {
    if (!person.canEdit) return err(403, 'this link is read-only');
    const b = await readJson(request);
    if (!b || !LEVELS.includes(b.level)) return err(400, 'level must be one of ' + LEVELS.join(', '));
    await env.DB.prepare('UPDATE people SET level = ?1 WHERE id = ?2').bind(b.level, person.id).run();
    return json({ ok: true, level: b.level });
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
