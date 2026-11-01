(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const A = window.AIRCRAFT;
  const byId = id => A.find(a => a.id === id);
  const img = key => `assets/img/${key}.jpg`;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const fmt = n => Number(n).toLocaleString("en-US");
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* ignore */ } }
  };

  const FLAGS = {
    us: '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="9.5" fill="#23315a"/><path d="M10 2.6l1.75 5.2h5.45l-4.4 3.2 1.7 5.2L10 13l-4.5 3.2 1.7-5.2-4.4-3.2h5.45z" fill="#fff"/></svg>',
    uk: '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="9.5" fill="#23315a"/><circle cx="10" cy="10" r="6.4" fill="#fff"/><circle cx="10" cy="10" r="3.4" fill="#b7322c"/></svg>',
    de: '<svg viewBox="0 0 20 20" aria-hidden="true"><rect width="20" height="20" rx="10" fill="#fff"/><path d="M8 3h4v5h5v4h-5v5H8v-5H3V8h5z" fill="#1a1a1a" stroke="#fff" stroke-width=".8"/></svg>',
    jp: '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="9.5" fill="#fff" stroke="#ccc"/><circle cx="10" cy="10" r="5.5" fill="#bc1f2c"/></svg>'
  };
  const NATIONS = [["all", "All"], ["us", "United States"], ["uk", "United Kingdom"], ["de", "Germany"], ["jp", "Japan"]];
  const ROLES = [["all", "All"], ["fighter", "Fighters"], ["naval", "Carrier"], ["heavy", "Twin-engine"], ["bomber", "Bombers"]];

  /* ---------- Top bar, progress, scrollspy ---------- */
  function initChrome() {
    const bar = $("#topbar"), prog = $("#progressBar"), heroMedia = $("#heroMedia");
    let ticking = false;
    const onScroll = () => {
      ticking = false;
      const y = window.scrollY, h = document.documentElement.scrollHeight - innerHeight;
      bar.classList.toggle("solid", y > 40); // go solid early so hero copy never scrolls under a transparent bar
      prog.style.transform = `scaleX(${h > 0 ? y / h : 0})`;
      if (!reduced && y < innerHeight * 1.2) heroMedia.style.transform = `translate3d(${mx}px, ${y * 0.28 + my}px, 0) scale(1.04)`;
    };
    let mx = 0, my = 0;
    window.addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
    if (!reduced && matchMedia("(hover: hover)").matches) {
      $(".hero").addEventListener("pointermove", e => {
        mx = (e.clientX / innerWidth - 0.5) * -18; my = (e.clientY / innerHeight - 0.5) * -12;
        if (!ticking) { ticking = true; requestAnimationFrame(onScroll); }
      });
    }
    onScroll();

    const links = $$(".navlinks a");
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (en.isIntersecting) links.forEach(l => l.setAttribute("aria-current", String(l.getAttribute("href") === "#" + en.target.id)));
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    $$("main section[id]").forEach(s => io.observe(s));

    // Sound toggle
    const st = $("#soundToggle");
    const saved = store.get("sound");
    const setSound = on => { st.setAttribute("aria-pressed", String(on)); window.EngineAudio.setEnabled(on); store.set("sound", on ? "1" : "0"); st.title = on ? "Mute engine sound" : "Turn engine sound on"; };
    setSound(saved !== "0");
    st.addEventListener("click", () => setSound(st.getAttribute("aria-pressed") !== "true"));
  }

  /* ---------- Anatomy ---------- */
  function initAnatomy() {
    const H = window.MUSTANG_HOTSPOTS;
    const host = $("#hotspots"), panel = $("#partPanel"), stage = $(".hotspot-stage");
    let cur = 0;
    H.forEach((h, i) => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "hs"; b.role = "tab";
      b.id = "hs-" + h.id;
      b.style.left = h.x + "%"; b.style.top = h.y + "%";
      b.setAttribute("aria-label", h.label);
      b.setAttribute("aria-controls", "partPanel");
      b.innerHTML = `<span class="hs-label" aria-hidden="true">${h.label}</span>`;
      b.addEventListener("click", () => select(i, true));
      b.addEventListener("keydown", e => {
        if (e.key === "ArrowRight" || e.key === "ArrowDown") { e.preventDefault(); select((cur + 1) % H.length, true, true); }
        if (e.key === "ArrowLeft" || e.key === "ArrowUp") { e.preventDefault(); select((cur - 1 + H.length) % H.length, true, true); }
      });
      host.appendChild(b);
    });
    function select(i, zoom, focus) {
      cur = i;
      const h = H[i];
      $$(".hs", host).forEach((b, j) => { b.setAttribute("aria-selected", String(j === i)); b.tabIndex = j === i ? 0 : -1; });
      if (focus) host.children[i].focus();
      stage.style.setProperty("--zx", h.x + "%"); stage.style.setProperty("--zy", h.y + "%");
      stage.classList.toggle("zoomed", !!zoom);
      // keep dots aligned with the zoomed image
      const s = zoom ? 1.35 : 1;
      $$(".hs", host).forEach((b, j) => {
        const p = H[j];
        b.style.left = (h.x + (p.x - h.x) * s) + "%";
        b.style.top = (h.y + (p.y - h.y) * s) + "%";
        b.style.visibility = (zoom && (h.x + (p.x - h.x) * s < 2 || h.x + (p.x - h.x) * s > 98)) ? "hidden" : "visible";
      });
      panel.setAttribute("aria-labelledby", "hs-" + h.id);
      panel.innerHTML = `
        <p class="pp-count">${i + 1} of ${H.length}</p>
        <h3>${h.title}</h3>
        <p>${h.text}</p>
        <div class="pp-figure"><strong>${h.figure}</strong><span>${h.figureNote}</span></div>
        <div class="pp-steps">
          <button type="button" data-d="-1">Previous part</button>
          <button type="button" data-d="1">Next part</button>
        </div>`;
      panel.querySelectorAll("[data-d]").forEach(btn => btn.addEventListener("click", () => select((cur + Number(btn.dataset.d) + H.length) % H.length, true)));
    }
    select(1, false);
    // Click on empty image area zooms back out
    stage.addEventListener("click", e => { if (e.target === stage.querySelector("img") || e.target === host) select(cur, !stage.classList.contains("zoomed")); });
  }

  /* ---------- Lineage ---------- */
  const BIG = {
    na73x: ["102 days", "from signed order to a rolled-out prototype airframe"],
    p51a: ["15,000 ft", "where the single-stage Allison engine began to run out of breath"],
    p51h: ["472 mph", "top speed of the lightest, fastest production Mustang"]
  };
  function initLineage() {
    const V = window.MUSTANG_VARIANTS, track = $("#lineageTrack"), body = $("#lineageBody");
    const fill = document.createElement("span"); fill.className = "fill"; track.appendChild(fill);
    V.forEach((v, i) => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "ln-node"; b.role = "tab"; b.id = "ln-" + v.id;
      b.innerHTML = `<span class="ln-dot">${String(v.year).slice(2)}</span><span class="ln-name">${v.label}</span><span class="ln-year">${v.year}</span>`;
      b.setAttribute("aria-label", `${v.label}, ${v.year}`);
      b.addEventListener("click", () => show(i));
      b.addEventListener("keydown", e => {
        if (e.key === "ArrowRight") { e.preventDefault(); show(Math.min(V.length - 1, cur + 1), true); }
        if (e.key === "ArrowLeft") { e.preventDefault(); show(Math.max(0, cur - 1), true); }
      });
      track.appendChild(b);
    });
    let cur = 3;
    function show(i, focus) {
      cur = i;
      const v = V[i], prev = V[i - 1];
      const nodes = $$(".ln-node", track);
      nodes.forEach((n, j) => { n.setAttribute("aria-selected", String(j === i)); n.classList.toggle("done", j <= i); n.tabIndex = j === i ? 0 : -1; });
      if (focus) nodes[i].focus();
      const firstDot = nodes[0].querySelector(".ln-dot"), dot = nodes[i].querySelector(".ln-dot");
      const tr = track.getBoundingClientRect();
      const span = (dot.getBoundingClientRect().left + 22) - (firstDot.getBoundingClientRect().left) + track.scrollLeft * 0;
      fill.style.width = Math.max(0, span) + "px";
      fill.style.left = (firstDot.getBoundingClientRect().left - tr.left + track.scrollLeft + 22) + "px";
      body.setAttribute("aria-labelledby", "ln-" + v.id);
      const media = v.photo
        ? `<img src="${img(v.photo)}" alt="${v.label} Mustang in flight" data-lightbox="${v.label}: ${v.title}">`
        : `<div class="noimg big"><strong>${BIG[v.id][0]}</strong><span>${BIG[v.id][1]}</span></div>`;
      const names = { engine: "Engine", speed: "Top speed", guns: "Guns", canopy: "Canopy" };
      body.innerHTML = `
        <div class="lb-media">${media}</div>
        <div class="lb-text">
          <h3>${v.title}</h3>
          <p>${v.text}</p>
          <dl class="lb-stats">${Object.keys(names).map(k => `<div><dt>${names[k]}</dt><dd class="${prev && prev.stats[k] !== v.stats[k] ? "changed" : ""}">${v.stats[k]}</dd></div>`).join("")}</dl>
        </div>`;
      body.classList.remove("is-swapping"); void body.offsetWidth; body.classList.add("is-swapping");
    }
    show(cur);
    let rw = innerWidth;
    addEventListener("resize", () => { if (innerWidth !== rw) { rw = innerWidth; layoutFill(); } });
    function layoutFill() {
      const nodes = $$(".ln-node", track), tr = track.getBoundingClientRect();
      const first = nodes[0].querySelector(".ln-dot").getBoundingClientRect(), dot = nodes[cur].querySelector(".ln-dot").getBoundingClientRect();
      fill.style.width = Math.max(0, dot.left + 22 - first.left) + "px";
      fill.style.left = (first.left - tr.left + track.scrollLeft + 22) + "px";
    }
  }

  /* ---------- Reach ---------- */
  function initReach() {
    const E = window.ESCORT, host = $("#reachChart");
    const W = 980, left = 190, right = 30, rowH = 64, top = 56;
    const maxMi = 800, x = mi => left + (mi / maxMi) * (W - left - right);
    const H = top + E.fighters.length * rowH + 30;
    let svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="reachDesc"><desc id="reachDesc">Bar chart of escort radius from East Anglia for four fighters.</desc>`;
    svg += `<rect x="${left}" y="${top - 10}" width="${W - left - right}" height="${E.fighters.length * rowH}" fill="#eef0ec" rx="6"/>`;
    E.targets.forEach((t, i) => {
      const tx = x(t.mi);
      svg += `<line class="t-line" x1="${tx}" x2="${tx}" y1="${top - 14}" y2="${top + E.fighters.length * rowH - 6}"/>`;
      svg += `<text class="t-label" x="${tx}" y="${top - 22 - (i % 2) * 18}" text-anchor="middle">${t.name}</text>`;
    });
    [0, 200, 400, 600, 800].forEach(m => { svg += `<text class="axis" x="${x(m)}" y="${H - 6}" text-anchor="middle">${m} mi</text>`; });
    E.fighters.forEach((f, i) => {
      const y = top + i * rowH;
      const color = f.id === "p51d" ? "#f2c230" : "#445063";
      svg += `<text class="f-label" x="${left - 16}" y="${y + 27}" text-anchor="end">${f.name}</text>`;
      svg += `<rect class="bar" data-i="${i}" x="${left}" y="${y + 8}" height="30" rx="4" fill="${color}" width="0"/>`;
      svg += `<text class="f-val" data-v="${i}" x="${left}" y="${y + 29}" fill="${f.id === "p51d" ? "#1a2333" : "#fff"}"></text>`;
    });
    svg += `</svg>`;
    host.innerHTML = svg + `<p class="reach-summary" id="reachSummary" aria-live="polite"></p>`;
    const set = tanks => {
      E.fighters.forEach((f, i) => {
        const mi = tanks ? f.tanks : f.internal;
        const bar = host.querySelector(`.bar[data-i="${i}"]`), val = host.querySelector(`[data-v="${i}"]`);
        const w = x(mi) - left;
        if (reduced) bar.setAttribute("width", w);
        else animateAttr(bar, "width", Number(bar.getAttribute("width")), w, 700);
        val.textContent = mi + " mi";
        val.setAttribute("x", left + w - 10); val.setAttribute("text-anchor", "end");
      });
      const reachBerlin = E.fighters.filter(f => (tanks ? f.tanks : f.internal) >= 580).map(f => f.name);
      $("#reachSummary").textContent = reachBerlin.length
        ? `With drop tanks, only the ${reachBerlin.join(" and ")} could escort bombers to Berlin and back.`
        : "On internal fuel alone, none of these fighters could cover a Berlin mission. Even the Ruhr was marginal for most.";
    };
    $$("#tankSeg button").forEach(b => b.addEventListener("click", () => {
      $$("#tankSeg button").forEach(x2 => x2.setAttribute("aria-checked", String(x2 === b)));
      set(b.dataset.tanks === "1");
    }));
    // Animate in when it scrolls into view
    let shown = false;
    new IntersectionObserver(en => { if (en[0].isIntersecting && !shown) { shown = true; set(true); } }, { threshold: 0.3 }).observe(host);
  }
  function animateAttr(el, attr, from, to, dur) {
    const t0 = performance.now();
    const ease = t => 1 - Math.pow(1 - t, 3);
    const f = now => { const t = Math.min(1, (now - t0) / dur); el.setAttribute(attr, from + (to - from) * ease(t)); if (t < 1) requestAnimationFrame(f); };
    requestAnimationFrame(f);
  }

  /* ---------- Hangar ---------- */
  const F = { nation: "all", role: "all", year: null, sort: "default" };
  function initHangar() {
    const mkChips = (host, list, key) => {
      list.forEach(([k, label]) => {
        const b = document.createElement("button");
        b.type = "button"; b.className = "chip"; b.dataset.k = k;
        b.setAttribute("aria-pressed", String(F[key] === k));
        b.innerHTML = (FLAGS[k] && key === "nation" ? FLAGS[k] : "") + `<span>${label}</span><span class="n"></span>`;
        b.addEventListener("click", () => { F[key] = k; $$(".chip", host).forEach(c => c.setAttribute("aria-pressed", String(c === b))); renderFleet(); });
        host.appendChild(b);
      });
    };
    mkChips($("#nationChips"), NATIONS, "nation");
    mkChips($("#roleChips"), ROLES, "role");
    $$("#nationChips .chip svg").forEach(s => { s.style.width = "18px"; s.style.height = "18px"; });
    const yr = $("#yearRange");
    yr.addEventListener("input", () => {
      const v = Number(yr.value);
      F.year = v === 1938 ? null : v;
      $("#yearOut").textContent = F.year ? F.year : "any year";
      yr.setAttribute("aria-valuetext", F.year ? String(F.year) : "Any year");
      renderFleet();
    });
    $("#sortSel").addEventListener("change", e => { F.sort = e.target.value; renderFleet(); });
    $("#clearFilters").addEventListener("click", clearFilters);

    const fleet = $("#fleet");
    A.forEach(a => {
      const li = document.createElement("li");
      li.dataset.id = a.id;
      li.innerHTML = `
        <button type="button" class="tile" aria-label="Open ${a.name}">
          <span class="tile-media">
            <img src="${img(a.photos[0].key)}" alt="" loading="lazy">
            <span class="tile-flag">${FLAGS[a.nationKey]}${a.nation}</span>
            <span class="tile-open" aria-hidden="true">Open dossier</span>
          </span>
          <span class="tile-body">
            <span class="tile-name">${a.name}</span>
            <span class="tile-role">${a.role}</span>
            <span class="tile-stats"><span><b>${a.specs.speed}</b> mph</span><span><b>${fmt(a.specs.range)}</b> mi range</span></span>
          </span>
        </button>`;
      li.querySelector(".tile").addEventListener("click", () => openDossier(a.id, true));
      fleet.appendChild(li);
    });
    renderFleet(true);
  }
  function clearFilters() {
    F.nation = "all"; F.role = "all"; F.year = null;
    $$("#nationChips .chip").forEach(c => c.setAttribute("aria-pressed", String(c.dataset.k === "all")));
    $$("#roleChips .chip").forEach(c => c.setAttribute("aria-pressed", String(c.dataset.k === "all")));
    $("#yearRange").value = 1938; $("#yearOut").textContent = "any year";
    renderFleet();
  }
  const matches = (a, f) =>
    (f.nation === "all" || a.nationKey === f.nation) &&
    (f.role === "all" || a.roleKey === f.role) &&
    (!f.year || (a.service[0] <= f.year && a.service[1] >= f.year));

  function renderFleet(first) {
    const fleet = $("#fleet");
    const items = $$("li", fleet);
    const before = new Map(items.map(li => [li.dataset.id, li.getBoundingClientRect()]));
    let list = A.filter(a => matches(a, F));
    const sorters = {
      speed: (a, b) => b.specs.speed - a.specs.speed,
      range: (a, b) => b.specs.range - a.specs.range,
      first: (a, b) => parseInt(a.firstFlight.slice(-4)) - parseInt(b.firstFlight.slice(-4)),
      name: (a, b) => a.name.localeCompare(b.name)
    };
    if (sorters[F.sort]) list = list.slice().sort(sorters[F.sort]);
    const ids = list.map(a => a.id);
    items.forEach(li => { li.hidden = !ids.includes(li.dataset.id); li.classList.remove("feature"); });
    ids.forEach(id => fleet.appendChild(fleet.querySelector(`li[data-id="${id}"]`)));
    if (F.sort === "default" && ids[0] === "p51d" && ids.length > 2) fleet.querySelector('li[data-id="p51d"]').classList.add("feature");

    // Chip counts reflect the other active filters
    $$("#nationChips .chip").forEach(c => { c.querySelector(".n").textContent = A.filter(a => matches(a, { ...F, nation: c.dataset.k })).length; });
    $$("#roleChips .chip").forEach(c => { c.querySelector(".n").textContent = A.filter(a => matches(a, { ...F, role: c.dataset.k })).length; });

    $("#resultCount").textContent = ids.length === A.length ? `Showing all ${A.length} aircraft` : `Showing ${ids.length} of ${A.length} aircraft`;
    $("#emptyState").hidden = ids.length > 0;

    if (first || reduced) return;
    // FLIP animation so tiles glide to their new places
    $$("li:not([hidden])", fleet).forEach(li => {
      const b = before.get(li.dataset.id), a = li.getBoundingClientRect();
      if (!b || !b.width) { li.animate([{ opacity: 0, transform: "scale(.96)" }, { opacity: 1, transform: "none" }], { duration: 320, easing: "cubic-bezier(.2,.7,.2,1)" }); return; }
      const dx = b.left - a.left, dy = b.top - a.top;
      if (dx || dy) li.animate([{ transform: `translate(${dx}px, ${dy}px)` }, { transform: "none" }], { duration: 420, easing: "cubic-bezier(.2,.7,.2,1)" });
    });
  }

  /* ---------- Dossier ---------- */
  const dlg = () => $("#dossier");
  let openId = null, photoIdx = 0, pushed = false, returnFocus = null;
  const MAX = { speed: 437, range: 2000, ceiling: 44000, climb: 4750, guns: 13 };
  function openDossier(id, push) {
    const a = byId(id); if (!a) return;
    if (!dlg().open) returnFocus = document.activeElement;
    openId = id; photoIdx = 0;
    const i = A.indexOf(a);
    const prev = A[(i - 1 + A.length) % A.length], next = A[(i + 1) % A.length];
    const meters = [
      ["Top speed", "speed", v => v + " mph"],
      ["Range", "range", v => fmt(v) + " mi"],
      ["Ceiling", "ceiling", v => fmt(v) + " ft"],
      ["Climb", "climb", v => fmt(v) + " ft/min"],
      ["Guns", "guns", v => v]
    ];
    const other = a.id === "p51d" ? "bf109" : "p51d";
    $("#dossierInner").innerHTML = `
      <div class="d-bar">
        <span class="d-crumb">Hangar, ${i + 1} of ${A.length}</span>
        <button type="button" class="icon-btn" data-go="${prev.id}" aria-label="Previous aircraft: ${prev.name}"><svg viewBox="0 0 24 24"><path d="M15 6l-6 6 6 6"/></svg></button>
        <button type="button" class="icon-btn" data-go="${next.id}" aria-label="Next aircraft: ${next.name}"><svg viewBox="0 0 24 24"><path d="M9 6l6 6-6 6"/></svg></button>
        <button type="button" class="icon-btn" data-close aria-label="Close"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
      </div>
      <div class="d-grid">
        <div class="d-gallery">
          <div class="d-main" id="dMain"></div>
          <p class="d-cap" id="dCap"></p>
          <div class="d-thumbs" role="group" aria-label="Photos">${a.photos.map((p, j) => `<button type="button" data-ph="${j}" aria-label="Photo ${j + 1}: ${p.caption}"><img src="${img(p.key)}" alt=""></button>`).join("")}</div>
        </div>
        <div>
          <div class="d-head">
            <span class="d-nation">${FLAGS[a.nationKey]}${a.nation}</span>
            <h2 id="dossierTitle">${a.name}</h2>
            <p>${a.role} by ${a.maker}. First flew ${a.firstFlight}; ${a.built} built.</p>
          </div>
          <div class="d-specs">${meters.map(([l, k, f]) => `<div class="meter"><span>${l}</span><span class="m-track"><span class="m-fill" style="width:${Math.min(100, a.specs[k] / MAX[k] * 100)}%"></span></span><b>${f(a.specs[k])}</b></div>`).join("")}</div>
          <dl class="d-facts">
            <div><dt>Engine</dt><dd>${a.engine}</dd></div>
            <div><dt>Armament</dt><dd>${a.armament}</dd></div>
            <div><dt>Crew</dt><dd>${a.crew}</dd></div>
            <div><dt>In service</dt><dd>${a.service[0]}–${a.service[1]}</dd></div>
          </dl>
        </div>
      </div>
      <div class="d-body">
        <div class="d-inside">
          <h3>${a.crew > 1 ? "Inside the aircraft" : "In the cockpit"}</h3>
          <p>${a.interior}</p>
          <div class="d-fact"><strong>Worth knowing</strong>${a.fact}</div>
        </div>
        <div class="d-pros">
          <h3>Verdict</h3>
          <h4>What it did well</h4>
          <ul class="pro">${a.strengths.map(s => `<li>${s}</li>`).join("")}</ul>
          <h4>Where it fell short</h4>
          <ul class="con">${a.weaknesses.map(s => `<li>${s}</li>`).join("")}</ul>
        </div>
      </div>
      <div class="d-actions">
        <button type="button" class="btn btn-small" data-compare="${other}">Compare with the ${byId(other).name}</button>
        ${a.id === "p51d" ? '<a class="btn btn-small" href="#cockpit" data-close>Fly the P-51D</a>' : ""}
      </div>`;
    const inner = $("#dossierInner");
    inner.scrollTop = 0;
    inner.querySelectorAll("[data-go]").forEach(b => b.addEventListener("click", () => openDossier(b.dataset.go, false)));
    inner.querySelectorAll("[data-close]").forEach(b => b.addEventListener("click", e => { if (b.tagName === "A") { e.preventDefault(); closeDossier(); setTimeout(() => $("#cockpit").scrollIntoView({ behavior: reduced ? "auto" : "smooth" }), 60); } else closeDossier(); }));
    inner.querySelectorAll("[data-ph]").forEach(b => b.addEventListener("click", () => setPhoto(Number(b.dataset.ph))));
    inner.querySelector("[data-compare]").addEventListener("click", e => {
      setCompare(a.id, e.currentTarget.dataset.compare);
      closeDossier();
      setTimeout(() => $("#compare").scrollIntoView({ behavior: reduced ? "auto" : "smooth" }), 60);
    });
    setPhoto(0);
    if (!dlg().open) { dlg().showModal(); document.documentElement.style.overflow = "hidden"; }
    const hash = "#aircraft/" + id;
    if (location.hash !== hash) {
      if (push && !pushed) { history.pushState({ dossier: id }, "", hash); pushed = true; }
      else history.replaceState({ dossier: id }, "", hash);
    }
    inner.querySelector("[data-close]").focus({ preventScroll: true });
  }
  function setPhoto(j) {
    const a = byId(openId); const n = a.photos.length;
    photoIdx = (j + n) % n;
    const p = a.photos[photoIdx];
    const main = $("#dMain");
    main.innerHTML = `<img src="${img(p.key)}" alt="${p.caption}" data-lightbox="${p.caption}">` +
      (n > 1 ? `<button type="button" class="icon-btn g-prev" aria-label="Previous photo"><svg viewBox="0 0 24 24"><path d="M15 6l-6 6 6 6"/></svg></button><button type="button" class="icon-btn g-next" aria-label="Next photo"><svg viewBox="0 0 24 24"><path d="M9 6l6 6-6 6"/></svg></button>` : "");
    $("#dCap").textContent = `${p.caption}  (${photoIdx + 1}/${n})`;
    $$(".d-thumbs button").forEach((b, k) => b.setAttribute("aria-current", String(k === photoIdx)));
    const pv = main.querySelector(".g-prev"), nx = main.querySelector(".g-next");
    pv && pv.addEventListener("click", () => setPhoto(photoIdx - 1));
    nx && nx.addEventListener("click", () => setPhoto(photoIdx + 1));
    // swipe
    let sx = null;
    main.onpointerdown = e => { sx = e.clientX; };
    main.onpointerup = e => { if (sx === null) return; const dx = e.clientX - sx; sx = null; if (Math.abs(dx) > 45) setPhoto(photoIdx + (dx < 0 ? 1 : -1)); };
  }
  function closeDossier(fromHistory) {
    if (!dlg().open) return;
    dlg().close();
  }
  function initDossier() {
    const d = dlg();
    d.addEventListener("close", () => {
      document.documentElement.style.overflow = "";
      if (location.hash.startsWith("#aircraft/")) {
        if (pushed) { pushed = false; history.back(); }
        else history.replaceState(null, "", "#hangar");
      }
      openId = null;
      if (returnFocus && document.contains(returnFocus)) returnFocus.focus({ preventScroll: true });
    });
    d.addEventListener("click", e => { if (e.target === d) closeDossier(); });
    d.addEventListener("keydown", e => {
      if (!openId) return;
      if (e.target.closest("select,input")) return;
      if (e.key === "ArrowRight") { setPhoto(photoIdx + 1); e.preventDefault(); }
      if (e.key === "ArrowLeft") { setPhoto(photoIdx - 1); e.preventDefault(); }
    });
    const route = () => {
      const m = location.hash.match(/^#aircraft\/([\w-]+)/);
      if (m && byId(m[1])) { if (openId !== m[1]) openDossier(m[1], false); }
      else if (d.open) { pushed = false; d.close(); }
    };
    addEventListener("popstate", route);
    addEventListener("hashchange", route);
    route();
  }

  /* ---------- Compare ---------- */
  const METRICS = [
    ["Top speed", "speed", v => v + " mph", true],
    ["Range", "range", v => fmt(v) + " mi", true],
    ["Ceiling", "ceiling", v => fmt(v) + " ft", true],
    ["Climb rate", "climb", v => fmt(v) + " ft/min", true],
    ["Horsepower", "power", v => fmt(v) + " hp", true],
    ["Guns", "guns", v => v, true],
    ["Max weight", "weight", v => fmt(v) + " lb", false]
  ];
  let cmp = { a: "p51d", b: "bf109" };
  function initCompare() {
    const sa = $("#cmpA"), sb = $("#cmpB");
    const opts = A.map(a => `<option value="${a.id}">${a.name}</option>`).join("");
    sa.innerHTML = opts; sb.innerHTML = opts;
    sa.addEventListener("change", () => { cmp.a = sa.value; renderCompare(); });
    sb.addEventListener("change", () => { cmp.b = sb.value; renderCompare(); });
    $("#swapBtn").addEventListener("click", e => {
      cmp = { a: cmp.b, b: cmp.a };
      e.currentTarget.classList.toggle("spin");
      renderCompare();
    });
    $("#butterfly").innerHTML = METRICS.map(([l, k]) => `
      <div class="bf-row" data-k="${k}">
        <div class="bf-side a"><span class="bf-bar"></span><span class="bf-val"></span></div>
        <div class="bf-metric">${l}</div>
        <div class="bf-side b"><span class="bf-bar"></span><span class="bf-val"></span></div>
      </div>`).join("");
    renderCompare();
  }
  function setCompare(a, b) { cmp = { a, b }; renderCompare(); }
  function renderCompare() {
    const a = byId(cmp.a), b = byId(cmp.b);
    $("#cmpA").value = a.id; $("#cmpB").value = b.id;
    $("#compareHeads").innerHTML = [a, b].map((x, i) => `
      <div class="ch ${i ? "ch-b" : ""}">
        <img src="${img(x.photos[0].key)}" alt="">
        <div><h3>${x.name}</h3><p>${x.role}, ${x.nation}</p></div>
      </div>`).join("");
    METRICS.forEach(([l, k, f, better]) => {
      const row = $(`.bf-row[data-k="${k}"]`);
      const va = a.specs[k], vb = b.specs[k], m = Math.max(va, vb);
      const sa = row.querySelector(".a"), sb = row.querySelector(".b");
      // Leave room for the value label inside the bar track
      sa.querySelector(".bf-bar").style.width = `${(va / m) * 70}%`;
      sb.querySelector(".bf-bar").style.width = `${(vb / m) * 70}%`;
      sa.querySelector(".bf-val").textContent = f(va);
      sb.querySelector(".bf-val").textContent = f(vb);
      sa.classList.toggle("win", better && va > vb);
      sb.classList.toggle("win", better && vb > va);
    });
    const v = [];
    const ds = a.specs.speed - b.specs.speed;
    v.push(ds === 0 ? `Both top out at about ${a.specs.speed} mph.` : `The ${ds > 0 ? a.name : b.name} is about ${Math.abs(ds)} mph faster.`);
    const ra = a.specs.range / b.specs.range;
    v.push(Math.abs(ra - 1) < 0.08 ? "Their ranges are roughly equal." : `The ${ra > 1 ? a.name : b.name} can fly ${(ra > 1 ? ra : 1 / ra).toFixed(1)}× as far.`);
    const dc = a.specs.climb - b.specs.climb;
    v.push(Math.abs(dc) < 150 ? "They climb at much the same rate." : `The ${dc > 0 ? a.name : b.name} climbs ${fmt(Math.abs(dc))} ft/min faster.`);
    if (a.id === b.id) { v.length = 0; v.push("Pick two different aircraft to compare them."); }
    $("#verdicts").innerHTML = v.map(t => `<li>${t}</li>`).join("");
  }

  /* ---------- Lightbox ---------- */
  function initLightbox() {
    const lb = $("#lightbox"), im = $("#lbImg"), cap = $("#lbCap");
    document.addEventListener("click", e => {
      const t = e.target.closest("img[data-lightbox], .cockpit-photos img");
      if (!t) return;
      im.src = t.currentSrc || t.src; im.alt = t.alt;
      cap.textContent = t.dataset.lightbox || (t.closest("figure") && t.closest("figure").querySelector("figcaption") ? t.closest("figure").querySelector("figcaption").textContent : t.alt);
      lb.showModal();
    });
    $("#lbClose").addEventListener("click", () => lb.close());
    lb.addEventListener("click", e => { if (e.target === lb || e.target === im) lb.close(); });
  }

  /* ---------- Credits ---------- */
  function initCredits() {
    const C = window.CREDITS || {};
    $("#creditList").innerHTML = Object.keys(C).sort().map(k => {
      const c = C[k];
      return `<li><a href="${c.page}" target="_blank" rel="noopener">${c.title.replace(/\.(jpe?g|png)$/i, "")}</a>${c.artist ? ` by ${c.artist}` : ""}, ${c.license}</li>`;
    }).join("");
  }

  if ("scrollRestoration" in history) history.scrollRestoration = "manual";
  document.addEventListener("DOMContentLoaded", () => {
    initChrome();
    initAnatomy();
    initLineage();
    window.Cockpit.init();
    window.FlightView && window.FlightView.init();
    initReach();
    initHangar();
    initCompare();
    initLightbox();
    initCredits();
    initDossier();
  });
})();
