// Admin page served at /api/eink/admin. Everything rendered with textContent (message text is untrusted).
export const ADMIN_HTML = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Frame Admin</title>
<style>
:root{--bg:#f7f5f0;--card:#fff;--ink:#1d1b18;--mute:#6b665d;--line:#ddd7cc;--acc:#8a5a2b;--bad:#a33}
@media (prefers-color-scheme:dark){:root{--bg:#171614;--card:#211f1c;--ink:#ece7de;--mute:#a39c90;--line:#3a3631;--acc:#d39a5c;--bad:#e77}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,sans-serif}
main{max-width:860px;margin:0 auto;padding:16px}h1{font-size:20px;margin:4px 0 12px}h2{font-size:17px;margin:0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin:12px 0}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:end}.row>label{flex:1 1 140px}
label{display:block;font-size:12px;color:var(--mute)}input,select,textarea,button{font:inherit;color:inherit}
input,select,textarea{width:100%;padding:7px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg)}
textarea{min-height:64px}button{padding:7px 12px;border:1px solid var(--acc);background:var(--acc);color:#fff;border-radius:6px;cursor:pointer}
button.ghost{background:transparent;color:var(--acc)}button.bad{border-color:var(--bad);background:transparent;color:var(--bad)}
.meta{color:var(--mute);font-size:13px}.tok{font-family:ui-monospace,monospace;user-select:all}
.msg{display:flex;justify-content:space-between;gap:8px;border-top:1px solid var(--line);padding:6px 0}
.screen{font-family:Georgia,serif;white-space:pre-wrap;background:#fff;color:#111;border:1px solid #999;border-radius:4px;padding:12px;aspect-ratio:5/3;overflow:auto;font-size:13px}
#err{color:var(--bad);min-height:1.2em}
</style></head><body><main>
<h1>E-ink frames</h1>
<div class="card row"><label>Admin key<input id="key" type="password" autocomplete="current-password"></label><button id="load">Load</button></div>
<div id="err"></div>
<div id="devices"></div>
<div class="card" id="addCard" hidden>
  <h2>Add a frame</h2>
  <div class="row"><label>For (admin only)<input id="n_name" maxlength="40"></label>
  <label>Town (looks up location)<input id="n_q" placeholder="Asheville"></label><button class="ghost" id="n_find">Find</button></div>
  <div class="row"><label>Match<select id="n_pick"></select></label>
  <label>Units<select id="n_units"><option>F</option><option>C</option></select></label>
  <label>Refresh times<input id="n_refresh" value="06:00,17:00"></label><button id="n_add">Add</button></div>
</div>
</main><script>
const $ = (id) => document.getElementById(id);
const API = location.pathname.replace(/\\/admin\\/?$/, '');
let key = '';
try { key = sessionStorage.getItem('eink-admin') || ''; } catch {}
$('key').value = key;
function el(tag, props = {}, ...kids) { const e = document.createElement(tag); Object.assign(e, props); for (const k of kids) e.append(k); return e; }
async function call(path, opts = {}) {
  const r = await fetch(API + path, { ...opts, headers: { 'x-admin-key': key, 'content-type': 'application/json', ...(opts.headers || {}) } });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.error || r.status);
  return j;
}
const show = (e) => { $('err').textContent = e ? String(e.message || e) : ''; };
function ago(ts) { if (!ts) return 'never'; const m = (Date.now() - Date.parse(ts.replace(' ', 'T') + 'Z')) / 60000; return m < 90 ? Math.round(m) + ' min ago' : m < 2880 ? Math.round(m / 60) + ' h ago' : Math.round(m / 1440) + ' d ago'; }
function screenText(f) {
  const w = f.weather ? \`\${f.weather.label}: \${f.weather.text}  \${f.weather.hi}° / \${f.weather.lo}°\${f.weather.pop != null ? '  ' + f.weather.pop + '%' : ''}\` : '(no weather)';
  const b = f.body.kind === 'poem' ? \`\${f.body.title}\\n\\n\${f.body.lines.join('\\n')}\\n\\n  - \${f.body.author}\` : \`\${f.body.text}\${f.body.from ? '\\n\\n  - ' + f.body.from : ''}\`;
  return \`\${w}        \${f.date}  \${f.place}\\n\${'-'.repeat(60)}\\n\\n\${b}\\n\\nupdated \${f.updated} - next wake in \${Math.round(f.sleep_s / 360) / 10} h\`;
}
async function load() {
  show(); key = $('key').value.trim();
  try { sessionStorage.setItem('eink-admin', key); } catch {}
  try {
    const list = await call('/devices');
    $('devices').replaceChildren(...list.map(deviceCard));
    $('addCard').hidden = false;
  } catch (e) { show(e); }
}
function deviceCard(d) {
  const card = el('div', { className: 'card' });
  const v = d.battery_mv ? (d.battery_mv / 1000).toFixed(2) + ' V' : '?';
  card.append(el('h2', { textContent: d.name + (d.place ? ' - ' + d.place : '') }),
    el('div', { className: 'meta', textContent: \`seen \${ago(d.last_seen)} - battery \${v} - wifi \${d.rssi ?? '?'} dBm - fw \${d.fw || '?'} - \${d.tz} - wakes \${d.refresh}\` }),
    el('div', { className: 'meta' }, 'token (flash with EINK_TOKEN=…): ', el('span', { className: 'tok', textContent: d.token })));
  const scr = el('div', { className: 'screen', hidden: true });
  const msgs = el('div');
  const body = el('textarea', { maxLength: 400, placeholder: 'Message (shows instead of the poem)' });
  const from = el('input', { maxLength: 40, placeholder: 'From' });
  const date = el('input', { type: 'date' });
  const pin = el('input', { type: 'checkbox', style: 'width:auto' });
  async function refreshMsgs() {
    const list = await call(\`/devices/\${d.id}/messages\`);
    msgs.replaceChildren(...list.map((m) => {
      const del = el('button', { className: 'bad', textContent: 'Delete' });
      del.onclick = async () => { try { await call('/messages/' + m.id, { method: 'DELETE' }); refreshMsgs(); } catch (e) { show(e); } };
      return el('div', { className: 'msg' }, el('div', {}, el('div', { textContent: m.body }),
        el('div', { className: 'meta', textContent: (m.show_on ? 'on ' + m.show_on : m.pinned ? 'pinned (every day)' : 'unscheduled (never shown)') + (m.from_name ? ' - from ' + m.from_name : '') })), del);
    }));
  }
  const add = el('button', { textContent: 'Add message' });
  add.onclick = async () => {
    try { await call(\`/devices/\${d.id}/messages\`, { method: 'POST', body: JSON.stringify({ body: body.value, from: from.value, show_on: date.value || null, pinned: pin.checked }) });
      body.value = ''; refreshMsgs(); } catch (e) { show(e); }
  };
  const prev = el('button', { className: 'ghost', textContent: 'Preview screen' });
  prev.onclick = async () => { try { scr.textContent = screenText(await call(\`/devices/\${d.id}/preview\`)); scr.hidden = false; } catch (e) { show(e); } };
  const units = el('select', {}, el('option', { textContent: 'F' }), el('option', { textContent: 'C' })); units.value = d.units;
  const refresh = el('input', { value: d.refresh });
  const save = el('button', { className: 'ghost', textContent: 'Save' });
  save.onclick = async () => { try { await call('/devices/' + d.id, { method: 'PATCH', body: JSON.stringify({ units: units.value, refresh: refresh.value }) }); load(); } catch (e) { show(e); } };
  const rm = el('button', { className: 'bad', textContent: 'Delete frame' });
  rm.onclick = async () => { if (confirm('Delete ' + d.name + "? Its frame will show 'not registered'.")) { try { await call('/devices/' + d.id, { method: 'DELETE' }); load(); } catch (e) { show(e); } } };
  card.append(el('div', { className: 'row' }, el('label', {}, 'Units', units), el('label', {}, 'Refresh times', refresh), save, prev, rm), scr,
    el('div', { className: 'row', style: 'margin-top:10px' }, el('label', { style: 'flex-basis:100%' }, 'New message', body),
      el('label', {}, 'From', from), el('label', {}, 'Show on (frame local date)', date), el('label', { style: 'flex:0 0 auto' }, 'Pin', pin), add), msgs);
  refreshMsgs().catch(show);
  return card;
}
let picks = [];
$('n_find').onclick = async () => {
  try { picks = await call('/geocode?q=' + encodeURIComponent($('n_q').value));
    $('n_pick').replaceChildren(...picks.map((p, i) => el('option', { value: i, textContent: \`\${p.label} (\${p.tz})\` })));
    if (!picks.length) show('No matches'); } catch (e) { show(e); }
};
$('n_add').onclick = async () => {
  const p = picks[$('n_pick').value];
  if (!p) return show('Find the town first');
  try { await call('/devices', { method: 'POST', body: JSON.stringify({ name: $('n_name').value, place: p.place, lat: p.lat, lon: p.lon, tz: p.tz, units: $('n_units').value, refresh: $('n_refresh').value }) });
    $('n_name').value = ''; load(); } catch (e) { show(e); }
};
$('load').onclick = load;
if (key) load();
</script></body></html>`;
