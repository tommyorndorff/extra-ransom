// RV temperature API: Cloudflare Worker + D1.
//
//   POST /reading     header X-Device-Key  {device?, temp_f, rail_v?, batt_v?, rssi?, lat?, lon?}
//   GET  /latest      header X-Read-Key    newest reading per device + active alerts
//   GET  /readings    header X-Read-Key    ?device=rv&hours=48 (max 720)
//
// A cron (every 15 min) checks for a missed check-in and cleans old rows. Alerts go to
// ntfy (push) and, as a backup, email. They fire on change, with a reminder every REMIND_H.

import { parseReading, evaluate, diffAlerts, buildEmail, safeEqual, TITLES } from './lib.js';

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });
const err = (status, message) => json({ error: message }, status);

const authed = (req, header, secret) => !!secret && safeEqual(req.headers.get(header) || '', secret);
const nowSec = () => Math.floor(Date.now() / 1000);

export function cfgOf(env) {
  return {
    lowTempF: Number(env.LOW_TEMP_F ?? 37),
    highTempF: Number(env.HIGH_TEMP_F ?? 95),
    lowRailV: Number(env.LOW_RAIL_V ?? 4.5),
    lowBattV: Number(env.LOW_BATT_V ?? 3.5),
    missedMin: Number(env.MISSED_MIN ?? 150),
    remindSec: Number(env.REMIND_H ?? 12) * 3600,
    keepDays: Number(env.KEEP_DAYS ?? 180),
  };
}

async function push(env, { title, body, priority }) {
  if (!env.NTFY_TOPIC) return false;
  // Header values must be plain ASCII, so the message text goes in the body.
  const res = await fetch(`https://ntfy.sh/${encodeURIComponent(env.NTFY_TOPIC)}`, {
    method: 'POST',
    headers: { Title: title, Priority: String(priority), Tags: priority >= 4 ? 'warning' : 'white_check_mark' },
    body,
  });
  return res.ok;
}

async function email(env, { title, body }) {
  if (!env.MAILER || !env.ALERT_EMAIL) return false;
  const { EmailMessage } = await import('cloudflare:email');
  const from = env.ALERT_FROM || 'rv-sensor@extra-ransom.net';
  const raw = buildEmail({ from, to: env.ALERT_EMAIL, subject: title, text: body });
  await env.MAILER.send(new EmailMessage(from, env.ALERT_EMAIL, raw));
  return true;
}

// Push first; email too, always (it is the backup, and a failed push must not hide an alert).
async function notify(env, n) {
  const results = await Promise.allSettled([push(env, n), email(env, n)]);
  results.forEach((r) => r.status === 'rejected' && console.error('notify failed:', r.reason?.message));
}

async function checkDevice(env, device, now = nowSec()) {
  const cfg = cfgOf(env);
  const latest = await env.DB.prepare('SELECT * FROM readings WHERE device = ? ORDER BY id DESC LIMIT 1').bind(device).first();
  const rows = (await env.DB.prepare('SELECT kind, last_sent FROM alert_state WHERE device = ?').bind(device).all()).results;
  const active = Object.fromEntries(rows.map((r) => [r.kind, r.last_sent]));
  const { send, cleared } = diffAlerts(evaluate(latest, now, cfg), active, now, cfg.remindSec);

  for (const a of send) {
    const prefix = a.type === 'reminder' ? 'Still: ' : '';
    await notify(env, { title: `${prefix}${TITLES[a.kind]}`, body: a.msg, priority: a.kind === 'low_temp' || a.kind === 'no_checkin' ? 5 : 4 });
    await env.DB.prepare('INSERT OR REPLACE INTO alert_state (device, kind, last_sent) VALUES (?, ?, ?)').bind(device, a.kind, now).run();
  }
  for (const kind of cleared) {
    await notify(env, { title: `Cleared: ${TITLES[kind]}`, body: 'Back to normal.', priority: 2 });
    await env.DB.prepare('DELETE FROM alert_state WHERE device = ? AND kind = ?').bind(device, kind).run();
  }
}

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    const path = url.pathname.replace(/^\/api\/rv/, '') || '/';

    if (req.method === 'POST' && path === '/reading') {
      if (!authed(req, 'X-Device-Key', env.DEVICE_KEY)) return err(401, 'bad device key');
      let body;
      try { body = await req.json(); } catch { return err(400, 'invalid JSON'); }
      const r = parseReading(body);
      if (r.error) return err(400, r.error);
      const v = r.value, ts = nowSec();
      await env.DB.prepare('INSERT INTO readings (device, ts, temp_f, rail_v, batt_v, rssi, lat, lon) VALUES (?, ?, ?, ?, ?, ?, ?, ?)')
        .bind(v.device, ts, v.temp_f, v.rail_v, v.batt_v, v.rssi, v.lat, v.lon).run();
      // Alerts run after the response so the modem can power down sooner.
      ctx.waitUntil(checkDevice(env, v.device, ts).catch((e) => console.error('checkDevice failed:', e.message)));
      return json({ ok: true, ts });
    }

    if (req.method === 'GET' && (path === '/latest' || path === '/readings')) {
      if (!authed(req, 'X-Read-Key', env.READ_KEY)) return err(401, 'bad read key');
      if (path === '/latest') {
        const latest = (await env.DB.prepare(
          'SELECT r.* FROM readings r JOIN (SELECT MAX(id) AS id FROM readings GROUP BY device) m ON r.id = m.id'
        ).all()).results;
        const alerts = (await env.DB.prepare('SELECT device, kind, last_sent FROM alert_state').all()).results;
        return json({ latest, alerts });
      }
      const device = url.searchParams.get('device') || 'rv';
      const hours = Math.min(Math.max(Number(url.searchParams.get('hours')) || 48, 1), 720);
      const rows = (await env.DB.prepare('SELECT ts, temp_f, rail_v, batt_v, rssi, lat, lon FROM readings WHERE device = ? AND ts >= ? ORDER BY id DESC')
        .bind(device, nowSec() - hours * 3600).all()).results;
      return json({ device, hours, readings: rows });
    }

    return err(404, 'not found');
  },

  // Cron: catch devices that went quiet, and prune old rows.
  async scheduled(_event, env) {
    const devices = (await env.DB.prepare('SELECT DISTINCT device FROM readings').all()).results;
    for (const { device } of devices) await checkDevice(env, device);
    await env.DB.prepare('DELETE FROM readings WHERE ts < ?').bind(nowSec() - cfgOf(env).keepDays * 86400).run();
  },
};
