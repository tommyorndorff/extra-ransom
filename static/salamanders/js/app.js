/* Salamanders of Western North Carolina — page logic. Data lives in data.js (window.SAL). */
(function () {
  "use strict";
  const D = window.SAL;
  const CREDITS = window.SAL_CREDITS || {};
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const img = key => `assets/img/${key}.jpg`;
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* ignore */ } }
  };
  const byId = Object.fromEntries(D.species.map(s => [s.id, s]));
  const famById = Object.fromEntries(D.families.map(f => [f.id, f]));
  const habById = Object.fromEntries(D.habitats.map(h => [h.id, h]));
  const ft = m => Math.round(m * 3.28084 / 10) * 10;
  const fmtElev = s => s.elev ? `${s.elev[0].toLocaleString()}–${s.elev[1].toLocaleString()} m` : "—";

  const STATUS = {
    E: { cls: "e", label: "NC Endangered" },
    T: { cls: "t", label: "NC Threatened" },
    SC: { cls: "sc", label: "NC Special Concern" }
  };
  function tags(s) {
    const out = [];
    if (s.nc && STATUS[s.nc]) out.push(`<span class="tag ${STATUS[s.nc].cls}" title="${STATUS[s.nc].label}">NC ${s.nc}</span>`);
    if (s.fedShort) out.push(`<span class="tag fed" title="${esc(s.fed)}">${esc(s.fedShort)}</span>`);
    if (s.endemic) out.push(`<span class="tag end" title="${esc(s.endemic)} endemic">${s.endemic === "NC" ? "NC endemic" : "S. App. endemic"}</span>`);
    return out.join("");
  }
  function statusColor(s) {
    if (s.nc === "E") return "var(--st-e)";
    if (s.nc === "T") return "var(--st-t)";
    if (s.nc === "SC") return "var(--st-sc)";
    return "var(--stream-2)";
  }

  /* ---------- Hero facts ---------- */
  function heroFacts() {
    const n = D.species.length;
    const plethodontids = D.species.filter(s => s.family === "plethodontidae").length;
    const endemics = D.species.filter(s => s.endemic).length;
    const listed = D.species.filter(s => s.nc).length;
    $("#heroFacts").innerHTML = [
      [n, "species treated here"],
      [plethodontids, "lungless plethodontids"],
      [endemics, "Southern Appalachian or NC endemics"],
      [listed, "carry NC protected status"]
    ].map(([v, l]) => `<li><b>${v}</b>${l}</li>`).join("");
  }

  /* ---------- Family bar ---------- */
  function familyBar() {
    const total = D.species.length;
    const counts = D.families.map(f => ({ f, n: D.species.filter(s => s.family === f.id).length })).filter(x => x.n);
    $("#familyBar").innerHTML = counts.map(({ f, n }) =>
      `<span style="flex:${n};background:${f.color}" title="${f.name}: ${n}">${n >= 3 ? n : ""}</span>`).join("");
    $("#familyKey").innerHTML = counts.map(({ f, n }) =>
      `<li><i class="sw" style="background:${f.color}"></i><span><b>${f.name}</b> (${f.common}): ${n} species</span></li>`).join("");
  }

  /* ---------- Elevation chart ---------- */
  const chartState = { group: store.get("sal-group") || "habitat", endemic: false };
  function elevChart() {
    const W = 1100, L = 250, R = 1080, top = 54, rowH = 20, gapH = 30;
    const E0 = 150, E1 = 2100;
    const x = e => L + (e - E0) / (E1 - E0) * (R - L);
    const groups = chartState.group === "habitat"
      ? D.habitats.map(h => ({ id: h.id, name: h.name, items: D.species.filter(s => s.habitat === h.id && s.elev) }))
      : D.families.map(f => ({ id: f.id, name: `${f.name} (${f.common})`, items: D.species.filter(s => s.family === f.id && s.elev) }));
    let y = top;
    const rows = [];
    groups.filter(g => g.items.length).forEach(g => {
      rows.push({ type: "g", y: y + 18, name: g.name });
      y += gapH;
      g.items.sort((a, b) => a.elev[0] - b.elev[0] || a.elev[1] - b.elev[1]).forEach(s => { rows.push({ type: "s", y, s }); y += rowH; });
      y += 6;
    });
    const H = y + 30;
    const zones = D.zones.map(z => `<rect x="${x(z.from)}" y="${top - 6}" width="${x(z.to) - x(z.from)}" height="${H - top - 24}" fill="${z.fill}"/>
      <text class="zone-label" x="${x(z.from) + 6}" y="${H - 12}">${z.name}</text>`).join("");
    const ticks = [];
    for (let e = 200; e <= 2000; e += 200) ticks.push(`<g class="axis"><line x1="${x(e)}" x2="${x(e)}" y1="${top - 6}" y2="${H - 24}"/>
      <text x="${x(e)}" y="${top - 30}" text-anchor="middle">${e.toLocaleString()} m</text>
      <text x="${x(e)}" y="${top - 16}" text-anchor="middle" opacity=".75">${ft(e).toLocaleString()} ft</text></g>`);
    const refs = D.refPeaks.map(p => `<g class="ref"><line x1="${x(p.m)}" x2="${x(p.m)}" y1="${top - 6}" y2="${H - 24}"/>
      <text x="${x(p.m) - 4}" y="${top + 8}" text-anchor="end">${p.name} ${p.m.toLocaleString()} m</text></g>`).join("");
    const body = rows.map(r => {
      if (r.type === "g") return `<text class="grp-label" x="12" y="${r.y}">${esc(r.name)}</text>`;
      const s = r.s, dim = chartState.endemic && !s.endemic ? ' opacity=".22"' : "";
      return `<g class="sp-row" data-id="${s.id}" tabindex="0" role="button" aria-label="${esc(s.sci)}, ${esc(s.common)}, ${fmtElev(s)}"${dim}>
        <rect class="hit" x="4" y="${r.y - 1}" width="${W - 8}" height="${rowH - 2}" fill="transparent" rx="3"/>
        <text class="sp-label" x="20" y="${r.y + 13}">${esc(s.sci)}</text>
        <rect class="bar" x="${x(s.elev[0])}" y="${r.y + 4}" width="${Math.max(4, x(s.elev[1]) - x(s.elev[0]))}" height="11" fill="${statusColor(s)}"/>
      </g>`;
    }).join("");
    $("#elevChart").innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="elevTitle">
      <title id="elevTitle">Approximate elevation range of each species in Western North Carolina, grouped by ${chartState.group}</title>
      ${zones}${ticks.join("")}${refs}${body}</svg>`;
    $$("#elevChart .sp-row").forEach(g => {
      g.addEventListener("click", () => openDossier(g.dataset.id));
      g.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openDossier(g.dataset.id); } });
    });
  }
  function chartControls() {
    $$("#groupSeg button").forEach(b => {
      b.setAttribute("aria-checked", String(b.dataset.g === chartState.group));
      b.addEventListener("click", () => {
        chartState.group = b.dataset.g; store.set("sal-group", b.dataset.g);
        $$("#groupSeg button").forEach(x => x.setAttribute("aria-checked", String(x === b)));
        elevChart();
      });
    });
    $("#endemicToggle").addEventListener("change", e => { chartState.endemic = e.target.checked; elevChart(); });
  }

  /* ---------- Range matrix ---------- */
  function matrix() {
    const cols = D.ranges;
    const head = `<thead><tr><th scope="col" style="text-align:left">Species</th>${cols.map(c => `<th scope="col" title="${esc(c.note)}">${esc(c.name)}</th>`).join("")}</tr></thead>`;
    const body = D.families.map(f => {
      const sp = D.species.filter(s => s.family === f.id && s.ranges);
      if (!sp.length) return "";
      return `<tr class="grp"><th class="g" colspan="${cols.length + 1}">${f.name}</th></tr>` + sp.map(s =>
        `<tr><th scope="row"><button type="button" data-id="${s.id}">${esc(s.sci)}</button></th>${cols.map(c => {
          const v = s.ranges[c.id];
          const label = v === 2 ? "present" : v === 1 ? "marginal or peripheral" : "absent";
          return `<td class="${v === 2 ? "on" : v === 1 ? "edge" : ""}"><span class="sr">${label}</span></td>`;
        }).join("")}</tr>`).join("");
    }).join("");
    $("#matrix").innerHTML = head + `<tbody>${body}</tbody>`;
    $$("#matrix button[data-id]").forEach(b => b.addEventListener("click", () => openDossier(b.dataset.id)));
  }

  /* ---------- Catalog ---------- */
  const filt = { q: "", family: "all", habitat: "all", status: "all", basin: "all", sort: "tax" };
  function catalogControls() {
    $("#fFamily").innerHTML = `<option value="all">All families</option>` + D.families.map(f => `<option value="${f.id}">${f.name}</option>`).join("");
    $("#fHabitat").innerHTML = `<option value="all">All microhabitats</option>` + D.habitats.map(h => `<option value="${h.id}">${h.name}</option>`).join("");
    $("#fBasin").innerHTML = `<option value="all">Any drainage</option>` + D.basins.map(b => `<option value="${b.id}">${b.name}</option>`).join("");
    const bind = (id, key) => $(id).addEventListener("input", e => { filt[key] = e.target.value; catalog(); });
    bind("#fQuery", "q"); bind("#fFamily", "family"); bind("#fHabitat", "habitat"); bind("#fStatus", "status"); bind("#fBasin", "basin"); bind("#fSort", "sort");
    $("#clearFilters").addEventListener("click", () => {
      Object.assign(filt, { q: "", family: "all", habitat: "all", status: "all", basin: "all" });
      $("#fQuery").value = ""; ["#fFamily", "#fHabitat", "#fStatus", "#fBasin"].forEach(s => { $(s).value = "all"; });
      catalog();
    });
  }
  let visible = D.species;
  function catalog() {
    const q = filt.q.trim().toLowerCase();
    visible = D.species.filter(s =>
      (filt.family === "all" || s.family === filt.family) &&
      (filt.habitat === "all" || s.habitat === filt.habitat) &&
      (filt.basin === "all" || (s.basins || []).includes(filt.basin)) &&
      (filt.status === "all" ||
        (filt.status === "listed" && (s.nc || s.fedShort)) ||
        (filt.status === "endemic" && s.endemic) ||
        (filt.status === s.nc)) &&
      (!q || [s.sci, s.common, s.formerly || "", s.range].join(" ").toLowerCase().includes(q)));
    const order = D.species.map(s => s.id);
    const sorters = {
      tax: (a, b) => order.indexOf(a.id) - order.indexOf(b.id),
      sci: (a, b) => a.sci.localeCompare(b.sci),
      common: (a, b) => a.common.localeCompare(b.common),
      high: (a, b) => (b.elev?.[1] || 0) - (a.elev?.[1] || 0),
      low: (a, b) => (a.elev?.[0] || 9e9) - (b.elev?.[0] || 9e9)
    };
    visible = visible.slice().sort(sorters[filt.sort]);
    $("#resultCount").textContent = `${visible.length} of ${D.species.length} species`;
    $("#emptyState").hidden = visible.length > 0;
    $("#catalogList").innerHTML = visible.map(s => `<li><button type="button" data-id="${s.id}">
        ${s.photo ? `<img class="thumb" src="${img(s.photo)}" alt="" loading="lazy">` : `<span class="thumb empty">no photo</span>`}
        <span><span class="sci">${esc(s.sci)}</span><span class="com">${esc(s.common)}</span></span>
        <span class="hab">${esc(habById[s.habitat]?.short || "")}</span>
        <span class="elv">${fmtElev(s)}</span>
        <span class="tags">${tags(s)}</span>
      </button></li>`).join("");
    $$("#catalogList button").forEach(b => b.addEventListener("click", () => openDossier(b.dataset.id)));
  }

  /* ---------- Status table ---------- */
  function statusTable() {
    const listed = D.species.filter(s => s.nc || s.fedShort || s.watch);
    $("#statusBody").innerHTML = listed.map(s => `<tr>
      <td class="sci">${esc(s.sci)}<span>${esc(s.common)}</span></td>
      <td>${s.nc ? `<span class="tag ${STATUS[s.nc].cls}">${STATUS[s.nc].label}</span>` : "—"}</td>
      <td>${esc(s.fed || "Not listed")}</td>
      <td>${esc([s.grank, s.srank].filter(Boolean).join(" / ") || "—")}</td>
      <td>${esc(s.iucn || "—")}</td>
      <td>${s.statusNote || ""}</td>
    </tr>`).join("");
  }

  /* ---------- Dossier ---------- */
  const dlg = $("#dossier");
  let current = null;
  function openDossier(id, push = true) {
    const s = byId[id]; if (!s) return;
    current = id;
    const f = famById[s.family], h = habById[s.habitat];
    const cr = s.photo && CREDITS[s.photo];
    const media = s.photo
      ? `<figure style="margin:0"><img src="${img(s.photo)}" alt="${esc(cr?.caption || s.common)}" data-lightbox="${esc(cr?.caption || s.sci)}"><figcaption>${esc(cr?.caption || "")}${cr ? ` Photo: ${esc(cr.artist)}, ${esc(cr.license)}.` : ""}</figcaption></figure>`
      : `<p class="no-photo">No freely licensed photo of this species was available. See the references for diagnostic illustrations.</p>`;
    const rows = [
      ["Range in WNC", s.range],
      ["Drainages", (s.basins || []).map(b => D.basins.find(x => x.id === b)?.short).filter(Boolean).join(", ")],
      ["Elevation", s.elev ? `${fmtElev(s)} (${ft(s.elev[0]).toLocaleString()}–${ft(s.elev[1]).toLocaleString()} ft)` : ""],
      ["Microhabitat", s.microhabitat || h?.name],
      ["Size", s.size],
      ["Reproduction", s.repro],
      ["Field ID", s.id_notes],
      ["Notes", s.notes],
      ["Status", [s.nc ? STATUS[s.nc].label : "", s.fed && s.fed !== "Not listed" ? s.fed : "", [s.grank, s.srank].filter(Boolean).join(" / "), s.iucn ? `IUCN ${s.iucn}` : ""].filter(Boolean).join("; ")]
    ].filter(([, v]) => v);
    const idx = visible.findIndex(x => x.id === id);
    const list = idx >= 0 ? visible : D.species;
    const i = list.findIndex(x => x.id === id);
    const prev = list[(i - 1 + list.length) % list.length], next = list[(i + 1) % list.length];
    $("#dossierInner").innerHTML = `<button type="button" class="d-close" aria-label="Close">&times;</button>
      <div class="d-inner${s.photo ? "" : " no-media"}">
        ${s.photo ? `<div class="d-media">${media}</div>` : ""}
        <div class="d-body">
          <p class="d-family">${esc(f?.name)} (${esc(f?.common)})</p>
          <h3 id="dossierTitle">${esc(s.sci)} <span class="auth">${esc(s.auth || "")}</span></h3>
          <p class="d-common">${esc(s.common)}${s.formerly ? ` — formerly treated as <i>${esc(s.formerly)}</i>` : ""}</p>
          <div class="d-tags">${tags(s)}</div>
          <dl>${rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("")}</dl>
          ${s.tax ? `<p class="tax">${s.tax}</p>` : ""}
          <div class="d-nav">
            <button type="button" data-go="${prev.id}">&larr; <i>${esc(prev.sci)}</i></button>
            <button type="button" data-go="${next.id}"><i>${esc(next.sci)}</i> &rarr;</button>
          </div>
        </div>
      </div>`;
    $(".d-close", dlg).addEventListener("click", closeDossier);
    $$("[data-go]", dlg).forEach(b => b.addEventListener("click", () => openDossier(b.dataset.go)));
    if (!dlg.open) dlg.showModal();
    $(".d-body", dlg).scrollTop = 0;
    if (push) history.replaceState(null, "", `#sp/${id}`);
  }
  function closeDossier() { dlg.close(); }
  dlg.addEventListener("close", () => { current = null; if (location.hash.startsWith("#sp/")) history.replaceState(null, "", location.pathname + location.search + "#catalog"); });
  dlg.addEventListener("click", e => { if (e.target === dlg) closeDossier(); });
  dlg.addEventListener("keydown", e => {
    if (!current) return;
    if (e.key === "ArrowRight") $$("[data-go]", dlg)[1]?.click();
    if (e.key === "ArrowLeft") $$("[data-go]", dlg)[0]?.click();
  });

  document.addEventListener("click", e => {
    const a = e.target.closest("a[data-sp]"); if (!a) return;
    e.preventDefault(); openDossier(a.dataset.sp);
  });

  /* ---------- Lightbox ---------- */
  const lb = $("#lightbox");
  document.addEventListener("click", e => {
    const t = e.target.closest("[data-lightbox]"); if (!t) return;
    $("#lbImg").src = t.currentSrc || t.src; $("#lbImg").alt = t.alt; $("#lbCap").textContent = t.dataset.lightbox;
    lb.showModal();
  });
  $("#lbClose").addEventListener("click", () => lb.close());
  lb.addEventListener("click", e => { if (e.target === lb) lb.close(); });

  /* ---------- Credits ---------- */
  function credits() {
    $("#creditList").innerHTML = Object.entries(CREDITS).map(([k, c]) =>
      `<li><a href="${esc(c.page)}">${esc(c.species || k)}</a> — ${esc(c.artist)}, ${c.licenseUrl ? `<a href="${esc(c.licenseUrl)}">${esc(c.license)}</a>` : esc(c.license)}</li>`).join("");
  }

  function refs() { $("#refs").innerHTML = D.refs.map(r => `<li>${r}</li>`).join(""); }

  /* ---------- Scroll spy ---------- */
  function spy() {
    const links = $$(".navlinks a");
    const map = new Map(links.map(a => [a.getAttribute("href").slice(1), a]));
    const io = new IntersectionObserver(entries => entries.forEach(en => {
      if (en.isIntersecting) { links.forEach(a => a.removeAttribute("aria-current")); map.get(en.target.id)?.setAttribute("aria-current", "true"); }
    }), { rootMargin: "-45% 0px -50% 0px" });
    map.forEach((_, id) => { const el = document.getElementById(id); if (el) io.observe(el); });
  }

  /* ---------- Init ---------- */
  heroFacts(); familyBar(); chartControls(); elevChart(); matrix(); catalogControls(); catalog(); statusTable(); credits(); refs(); spy();
  const m = location.hash.match(/^#sp\/([\w-]+)/);
  if (m && byId[m[1]]) openDossier(m[1], false);
  window.addEventListener("hashchange", () => { const h = location.hash.match(/^#sp\/([\w-]+)/); if (h) openDossier(h[1], false); });
})();
