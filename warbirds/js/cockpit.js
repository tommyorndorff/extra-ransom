/* P-51D cockpit simulator: simplified but physically plausible. */
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const approach = (v, target, rate, dt) => v + (target - v) * (1 - Math.exp(-rate * dt));

  const INFO = {
    asi: { title: "Airspeed indicator", text: "Shows indicated airspeed: how hard the air is pushing on the pitot tube, not true speed over the ground. At 25,000 ft the air is less than half as dense as at sea level, so a Mustang doing 437 mph true reads only about 290 mph here.", limits: "Never exceed 505 mph indicated. Stall around 100 mph clean, lower with flaps." },
    ai: { title: "Gyro horizon", text: "A spinning gyroscope holds an artificial horizon level while the aircraft moves around it. In cloud, it was the only reliable way to tell up from down. Pilots were taught to trust it over their own sense of balance, which lies in a turn.", limits: "The gyro could tumble in aerobatics beyond about 100° of bank or 60° of pitch." },
    alt: { title: "Altimeter", text: "A barometer calibrated in feet. The long hand counts hundreds, the short hand thousands, and the small yellow hand tens of thousands. Bomber escort usually meant 25,000 to 30,000 ft, where the B-17s flew.", limits: "Service ceiling about 41,900 ft. Above about 10,000 ft pilots needed oxygen." },
    hdg: { title: "Directional gyro", text: "A gyro-stabilised compass card that does not swing in turns the way a magnetic compass does. Pilots reset it against the magnetic compass in straight, level flight every 15 minutes or so, because it slowly drifted.", limits: "Bank the aircraft to turn; the turn rate depends on bank angle and speed." },
    vsi: { title: "Vertical speed indicator", text: "Shows how fast you are climbing or descending in thousands of feet per minute. A P-51D at full power could climb at about 3,200 ft/min, so it took around eight minutes to reach the bombers' altitude.", limits: "The needle lags a few seconds behind changes in pitch." },
    map: { title: "Manifold pressure", text: "The Mustang pilot's main power gauge. It measures the pressure of the fuel-air mixture the supercharger pushes into the cylinders, in inches of mercury. Watch it fall as you climb, then jump when the supercharger shifts into high blower at about 19,500 ft.", limits: "Cruise 30–46 inHg. Military power 61 inHg for 15 minutes. War emergency 67 inHg for 5 minutes." },
    tach: { title: "Tachometer", text: "Engine speed in hundreds of RPM. The propeller governor holds RPM constant by changing blade angle, so the pilot set power with two levers: throttle for manifold pressure and propeller for RPM. Here they are linked for simplicity.", limits: "Cruise around 2,400 rpm. Maximum 3,000 rpm." },
    coolant: { title: "Coolant temperature", text: "The Merlin is liquid-cooled, so this gauge was watched closely. On the ground there is little airflow through the radiator and the engine heats up fast, which is why pilots taxied quickly and took off without delay. In the air, speed cools it.", limits: "Normal 100–110 °C. Maximum 121 °C. A hit to the cooling system usually meant minutes before the engine seized." }
  };

  const S = {};
  function resetState() {
    Object.assign(S, {
      battery: false, fuel: false, mags: false, engineOn: false, cranking: 0,
      throttle: 0, rpm: 0, map: 29.92, tas: 0, ias: 0, alt: 0, vs: 0, vsShown: 0,
      pitch: 0, bank: 0, hdg: 270, coolant: 15, onGround: true, fuelGal: 269,
      highBlower: false, stall: false, stickX: 0, stickY: 0, timeScale: S.timeScale || 4
    });
  }
  resetState();

  const sigma = h => Math.pow(1 - 6.875e-6 * h, 4.256);       // density ratio
  const ambientMAP = h => 29.92 * Math.pow(1 - 6.875e-6 * h, 5.256);
  function availableMAP(h, high) {
    if (!high) return h < 12000 ? 61 : 61 - (h - 12000) * 0.002;
    return h < 25000 ? 61 : 61 - (h - 25000) * 0.002;
  }
  function vMax(h) { return h <= 25000 ? 375 + 62 * (h / 25000) : 437 - (h - 25000) * 0.006; }

  let gauges = {}, gaugeBtns = {}, visible = false, last = 0, lastLabel = 0;
  const keys = new Set();
  let dragging = false;

  function build() {
    const G = window.Gauges;
    const host = $("#gauges");
    const defs = [
      ["asi", "Airspeed", () => G.dial({ min: 0, max: 500, a0: -160, a1: 160, major: 50, minor: 10, fontSize: 14, title: "AIRSPEED", unit: "MPH", arcs: [{ from: 100, to: 400, color: "#3aa35b" }, { from: 400, to: 500, color: "#d9a520" }] })],
      ["ai", "Gyro horizon", () => G.attitude()],
      ["alt", "Altimeter", () => G.altimeter()],
      ["hdg", "Directional gyro", () => G.heading()],
      ["vsi", "Vertical speed", () => G.dial({ min: -6000, max: 6000, a0: -260, a1: 80, major: 1000, minor: 500, fontSize: 15, fmt: v => Math.abs(v / 1000), title: "CLIMB", unit: "×1000 FT/MIN" })],
      ["map", "Manifold pressure", () => G.dial({ min: 10, max: 75, a0: -140, a1: 140, major: 10, minor: 2, fontSize: 16, title: "MANIFOLD", unit: "IN HG", arcs: [{ from: 25, to: 46, color: "#3aa35b" }, { from: 46, to: 61, color: "#d9a520" }, { from: 61, to: 67, color: "#d0382c" }] })],
      ["tach", "Tachometer", () => G.dial({ min: 0, max: 4500, a0: -140, a1: 140, major: 500, minor: 100, fontSize: 15, fmt: v => v / 100, title: "TACH", unit: "RPM ×100", arcs: [{ from: 1600, to: 2700, color: "#3aa35b" }, { from: 2700, to: 3000, color: "#d9a520" }, { from: 3000, to: 3080, color: "#d0382c" }] })],
      ["coolant", "Coolant temperature", () => G.dial({ min: 0, max: 150, a0: -130, a1: 130, major: 30, minor: 10, fontSize: 15, title: "COOLANT", unit: "°C", arcs: [{ from: 60, to: 110, color: "#3aa35b" }, { from: 110, to: 121, color: "#d9a520" }, { from: 121, to: 150, color: "#d0382c" }] })]
    ];
    defs.forEach(([id, name, make]) => {
      const btn = document.createElement("button");
      btn.type = "button"; btn.className = "gauge"; btn.dataset.id = id;
      btn.setAttribute("aria-pressed", "false");
      btn.setAttribute("aria-label", name);
      const g = make();
      btn.appendChild(g.svg);
      host.appendChild(btn);
      gauges[id] = g; gaugeBtns[id] = btn;
      btn.addEventListener("click", () => showInfo(id));
    });
  }

  function showInfo(id) {
    Object.values(gaugeBtns).forEach(b => b.setAttribute("aria-pressed", String(b.dataset.id === id)));
    const i = INFO[id];
    $("#instrumentInfo").innerHTML = `<h3>${i.title}</h3><p>${i.text}</p><p class="limits">${i.limits}</p>`;
  }

  /* ---------- Start-up ---------- */
  const hint = t => { const h = $("#startupHint"); if (h.textContent !== t) h.textContent = t; };
  function syncSwitches() {
    document.querySelectorAll(".switch").forEach(b => b.setAttribute("aria-pressed", String(S[b.dataset.switch])));
    const ready = S.battery && S.fuel && S.mags;
    const st = $("#starter");
    if (S.engineOn && document.activeElement === st) $("#throttle").focus({ preventScroll: true });
    st.disabled = !ready || S.engineOn;
    st.classList.toggle("running", S.engineOn);
    st.firstElementChild.textContent = S.engineOn ? "Engine running" : "Hold to crank";
  }
  function bindStartup() {
    document.querySelectorAll(".switch").forEach(b => b.addEventListener("click", () => {
      const k = b.dataset.switch;
      S[k] = !S[k];
      if ((k === "mags" || k === "fuel") && !S[k] && S.engineOn) { S.engineOn = false; window.EngineAudio.stop(); }
      syncSwitches();
    }));
    const st = $("#starter"), fill = st.querySelector(".starter-fill");
    let holding = false, t0 = 0, raf = 0;
    const tick = now => {
      if (!holding) return;
      const p = clamp((now - t0) / 1600, 0, 1);
      fill.style.transform = `scaleX(${p})`;
      S.cranking = 1;
      if (p >= 1) { holding = false; S.cranking = 0; fill.style.transform = "scaleX(0)"; S.engineOn = true; window.EngineAudio.cough(); syncSwitches(); return; }
      raf = requestAnimationFrame(tick);
    };
    const down = e => {
      if (st.disabled) return;
      e.preventDefault();
      window.EngineAudio.start();
      holding = true; t0 = performance.now(); raf = requestAnimationFrame(tick);
      if (e.pointerId !== undefined) st.setPointerCapture(e.pointerId);
    };
    const up = () => { if (!holding) return; holding = false; S.cranking = 0; cancelAnimationFrame(raf); fill.style.transform = "scaleX(0)"; };
    st.addEventListener("pointerdown", down);
    st.addEventListener("pointerup", up);
    st.addEventListener("pointercancel", up);
    st.addEventListener("keydown", e => { if ((e.key === " " || e.key === "Enter") && !e.repeat) down(e); });
    st.addEventListener("keyup", e => { if (e.key === " " || e.key === "Enter") up(); });
  }

  /* ---------- Controls ---------- */
  function setThrottle(v) {
    S.throttle = clamp(v, 0, 1);
    const t = $("#throttle");
    t.value = Math.round(S.throttle * 100);
    const label = S.throttle < 0.02 ? "Idle" : S.throttle > 0.98 ? "Full" : Math.round(S.throttle * 100) + "%";
    $("#throttleOut").textContent = label;
    t.setAttribute("aria-valuetext", label);
  }
  function bindControls() {
    const t = $("#throttle");
    t.addEventListener("input", () => setThrottle(t.value / 100));
    const pad = $("#stickPad"), knob = $("#stickKnob");
    const fromEvent = e => {
      const r = pad.getBoundingClientRect();
      let x = (e.clientX - r.left) / r.width * 2 - 1, y = (e.clientY - r.top) / r.height * 2 - 1;
      const m = Math.hypot(x, y); if (m > 1) { x /= m; y /= m; }
      S.stickX = x; S.stickY = y;
    };
    pad.addEventListener("pointerdown", e => { dragging = true; pad.setPointerCapture(e.pointerId); fromEvent(e); });
    pad.addEventListener("pointermove", e => { if (dragging) fromEvent(e); });
    const end = () => { dragging = false; };
    pad.addEventListener("pointerup", end); pad.addEventListener("pointercancel", end);
    pad.addEventListener("keydown", e => {
      const map = { ArrowUp: 1, ArrowDown: 1, ArrowLeft: 1, ArrowRight: 1 };
      if (map[e.key]) { keys.add(e.key); e.preventDefault(); }
      if (e.key === "w" || e.key === "PageUp") { setThrottle(S.throttle + 0.05); e.preventDefault(); }
      if (e.key === "s" || e.key === "PageDown") { setThrottle(S.throttle - 0.05); e.preventDefault(); }
    });
    pad.addEventListener("keyup", e => keys.delete(e.key));
    pad.addEventListener("blur", () => keys.clear());
    S._renderKnob = () => {
      const r = pad.clientWidth / 2 - 26;
      knob.style.transform = `translate(${S.stickX * r}px, ${S.stickY * r}px)`;
    };

    document.querySelectorAll("#timeSeg button").forEach(b => b.addEventListener("click", () => {
      document.querySelectorAll("#timeSeg button").forEach(x => x.setAttribute("aria-checked", String(x === b)));
      S.timeScale = Number(b.dataset.t);
    }));
    $("#resetSim").addEventListener("click", () => {
      window.EngineAudio.stop(); const ts = S.timeScale; resetState(); S.timeScale = ts; setThrottle(0); syncSwitches(); window.FlightView && window.FlightView.reset();
    });
  }

  /* ---------- Simulation ---------- */
  function step(dt) {
    const ts = S.timeScale;
    // Stick: keyboard or drag, else spring to centre
    if (!dragging) {
      let kx = 0, ky = 0;
      if (keys.has("ArrowLeft")) kx -= 1; if (keys.has("ArrowRight")) kx += 1;
      if (keys.has("ArrowUp")) ky -= 1; if (keys.has("ArrowDown")) ky += 1;
      S.stickX = approach(S.stickX, kx * 0.8, kx ? 4 : 6, dt);
      S.stickY = approach(S.stickY, ky * 0.8, ky ? 4 : 6, dt);
    }

    // Engine
    const ambient = ambientMAP(S.alt);
    if (S.highBlower ? S.alt < 17500 : S.alt > 19500) S.highBlower = !S.highBlower;
    if (S.fuelGal <= 0) S.engineOn = false;
    const rpmTarget = S.engineOn ? 1200 + S.throttle * 1800 : (S.cranking ? 300 : 0);
    S.rpm = approach(S.rpm, rpmTarget, S.engineOn ? 1.6 : 0.8, dt);
    const idleMAP = ambient * 0.52;
    const avail = Math.max(idleMAP, availableMAP(S.alt, S.highBlower));
    const mapTarget = S.engineOn ? idleMAP + S.throttle * (Math.min(avail, 61) - idleMAP) : ambient;
    S.map = approach(S.map, mapTarget, 2.5, dt);
    const P = S.engineOn ? clamp((S.map - 15) / 46, 0, 1.05) * (S.rpm / 3000) : 0;

    // Attitude
    const stallNow = !S.onGround && S.ias < 95;
    S.stall = stallNow;
    let pitchTarget = S.stickY * 16, bankTarget = S.stickX * 62;
    if (S.onGround) {
      bankTarget = 0;
      pitchTarget = S.ias > 105 && S.stickY > 0.15 ? Math.min(pitchTarget, 8) : 0;
    }
    if (stallNow) pitchTarget = Math.min(pitchTarget, -6);
    S.pitch = approach(S.pitch, pitchTarget, 1.2, dt);
    S.bank = approach(S.bank, bankTarget, 1.5, dt);
    if (S.onGround && S.pitch > 1 && S.ias > 105) S.onGround = false;

    // Speed (true airspeed)
    let vTarget;
    if (S.onGround) vTarget = P * 190;
    else vTarget = vMax(S.alt) * Math.cbrt(Math.max(P, 0.001)) - S.pitch * 7 - Math.abs(S.bank) * 0.4;
    vTarget = Math.max(0, vTarget);
    S.tas = approach(S.tas, vTarget, S.onGround ? 0.18 : 0.22, dt);
    S.ias = S.tas * Math.sqrt(sigma(S.alt));

    // Vertical
    if (!S.onGround) {
      const gamma = (S.pitch * Math.PI) / 180;
      S.vs = S.tas * 88 * Math.sin(gamma) - (stallNow ? 1500 : 0);
      S.alt += (S.vs / 60) * dt * ts;
      if (S.alt <= 0) { S.alt = 0; S.onGround = true; S.pitch = 0; S.bank = 0; S.vs = 0; }
      if (S.alt > 42500) S.alt = 42500;
      // Heading change from bank
      const v = Math.max(S.tas * 0.447, 30);
      const rate = (9.81 * Math.tan((S.bank * Math.PI) / 180)) / v * (180 / Math.PI);
      S.hdg = (S.hdg + rate * dt * Math.min(ts, 4) + 360) % 360;
    } else S.vs = 0;
    S.vsShown = approach(S.vsShown, S.vs, 0.8, dt);

    // Coolant
    const cTarget = S.engineOn ? 85 + 40 * P - Math.min(S.ias, 420) / 400 * 30 + (S.onGround ? 18 : 0) : 15;
    S.coolant = approach(S.coolant, cTarget, 0.05 * Math.min(ts, 4), dt);

    // Fuel
    if (S.engineOn) S.fuelGal = Math.max(0, S.fuelGal - (20 + P * 130) / 3600 * dt * ts);
  }

  function render(now) {
    gauges.asi.set(S.ias);
    gauges.ai.set(S.pitch, S.bank);
    gauges.alt.set(S.alt);
    gauges.hdg.set(S.hdg);
    gauges.vsi.set(S.vsShown);
    gauges.map.set(S.map);
    gauges.tach.set(S.rpm);
    gauges.coolant.set(S.coolant);
    S._renderKnob && S._renderKnob();
    $("#lampBlower").dataset.on = String(S.highBlower);
    $("#lampCoolant").dataset.on = String(S.coolant > 121);
    $("#lampGround").dataset.on = String(S.onGround);

    const r = $("#readout");
    const cells = [
      ["Indicated", Math.round(S.ias) + " mph"],
      ["True airspeed", Math.round(S.tas) + " mph"],
      ["Altitude", Math.round(S.alt).toLocaleString() + " ft"],
      ["Climb", (S.vsShown >= 0 ? "+" : "−") + Math.abs(Math.round(S.vsShown / 10) * 10).toLocaleString() + " ft/min"],
      ["Heading", String(Math.round(S.hdg) % 360).padStart(3, "0") + "°"],
      ["Fuel", Math.round(S.fuelGal) + " gal"]
    ];
    if (!r.children.length) r.innerHTML = cells.map(c => `<div><span>${c[0]}</span><strong></strong></div>`).join("");
    cells.forEach((c, i) => { const s = r.children[i].lastElementChild; if (s.textContent !== c[1]) s.textContent = c[1]; });

    // Coaching
    if (!S.engineOn && !(S.battery && S.fuel && S.mags)) hint(S.fuelGal <= 0 ? "Out of fuel. Reset to try again." : "Flip the three switches, then press and hold the starter.");
    else if (!S.engineOn) hint("Press and hold the starter until the engine catches.");
    else if (S.onGround && S.throttle < 0.5) hint("Engine running. Push the throttle up to full power.");
    else if (S.onGround && S.ias < 105) hint(S.coolant > 115 ? "Coolant is climbing on the ground. Get airborne." : "Accelerating. Pull back on the stick once you pass 110 mph.");
    else if (S.onGround) hint("Pull back on the stick to lift off.");
    else if (S.stall) hint("Stall! Lower the nose and add power.");
    else if (S.coolant > 121) hint("Coolant over the limit. Ease off the throttle or lower the nose to gain speed.");
    else if (!S.highBlower && S.alt > 12000) hint("Notice the manifold pressure falling. Keep climbing past 19,500 ft.");
    else if (S.highBlower && S.alt < 26000) hint("High blower engaged: manifold pressure jumped back to 61 inHg. Climb to 25,000 ft and compare indicated with true airspeed.");
    else if (S.alt >= 26000) hint("Escort altitude. True airspeed is far higher than indicated in this thin air. Bank to turn.");
    else hint("Airborne. Hold the stick back gently to climb at about 170 mph indicated.");

    window.EngineAudio.set(S.rpm, P_for_audio());
    if (now - lastLabel > 1000) {
      lastLabel = now;
      gaugeBtns.asi.setAttribute("aria-label", `Airspeed ${Math.round(S.ias)} mph`);
      gaugeBtns.alt.setAttribute("aria-label", `Altimeter ${Math.round(S.alt)} feet`);
      gaugeBtns.map.setAttribute("aria-label", `Manifold pressure ${S.map.toFixed(0)} inches`);
      gaugeBtns.tach.setAttribute("aria-label", `Tachometer ${Math.round(S.rpm)} rpm`);
      gaugeBtns.coolant.setAttribute("aria-label", `Coolant ${Math.round(S.coolant)} degrees`);
      gaugeBtns.vsi.setAttribute("aria-label", `Vertical speed ${Math.round(S.vsShown)} feet per minute`);
      gaugeBtns.hdg.setAttribute("aria-label", `Heading ${Math.round(S.hdg)} degrees`);
      gaugeBtns.ai.setAttribute("aria-label", `Gyro horizon, pitch ${Math.round(S.pitch)}, bank ${Math.round(S.bank)} degrees`);
    }
  }
  const P_for_audio = () => (S.engineOn ? clamp(S.throttle, 0, 1) : 0);

  function loop(now) {
    const dt = Math.min(0.05, (now - (last || now)) / 1000);
    last = now;
    step(dt);
    try { if (window.FlightView) window.FlightView.frame(dt, S, now); } catch (e) { console.error(e); }
    render(now);
    if (visible) requestAnimationFrame(loop); else last = 0;
  }

  function init() {
    if (!$("#gauges")) return;
    build(); bindStartup(); bindControls(); syncSwitches(); setThrottle(0);
    render(0);
    const io = new IntersectionObserver(entries => {
      const v = entries[0].isIntersecting;
      if (v && !visible) { visible = true; requestAnimationFrame(loop); }
      if (!v) { visible = false; window.EngineAudio.set(0, 0); }
    }, { threshold: 0.05 });
    io.observe($("#cockpit"));
  }

  function setTime(t) {
    S.timeScale = t;
    document.querySelectorAll("#timeSeg button").forEach(x => x.setAttribute("aria-checked", String(Number(x.dataset.t) === t)));
  }
  function setStick(x, y, drag) {
    dragging = drag;
    if (x !== null) { S.stickX = x; S.stickY = y; }
  }
  function key(e, down) {
    const map = { ArrowUp: 1, ArrowDown: 1, ArrowLeft: 1, ArrowRight: 1 };
    if (map[e.key]) { e.preventDefault(); down ? keys.add(e.key) : keys.delete(e.key); }
    if (down && (e.key === "w" || e.key === "PageUp")) { setThrottle(S.throttle + 0.05); e.preventDefault(); }
    if (down && (e.key === "s" || e.key === "PageDown")) { setThrottle(S.throttle - 0.05); e.preventDefault(); }
  }
  function airStart() {
    const ts = S.timeScale;
    resetState();
    Object.assign(S, { battery: true, fuel: true, mags: true, engineOn: true, rpm: 2700, map: 46, throttle: 0.75,
      alt: 20000, tas: 380, onGround: false, highBlower: true, coolant: 98, hdg: 90, timeScale: ts });
    S.ias = S.tas * Math.sqrt(sigma(S.alt));
    window.EngineAudio.start();
    setThrottle(0.75); syncSwitches();
  }
  window.Cockpit = { init, showInfo, setStick, key, airStart, setTime, state: S };
})();
