/* Out-the-windscreen view + working K-14 gyro gunsight.
   Ground is rendered per-pixel (mode-7 style) into a small offscreen buffer,
   then rotated for bank. Clouds, the practice target, tracers and smoke are
   projected in 3D on top. The gunsight is drawn fixed to the aircraft. */
(function () {
  const DEG = Math.PI / 180;
  const FTS = 1.46667;                 // ft/s per mph
  const TEX = 512;
  let TILE_FT = 8000;                  // world size of one texture tile; varies by scene

  /* Scenes: terrain, sky, haze and cloud settings */
  const SCENES = {
    england: { label: "East Anglia, summer 1944", tex: "fields", tile: 8000,
      palette: ["#6f9150", "#86a35a", "#9fa65f", "#668a47", "#b4a46a", "#5d7f40", "#91a85e", "#a99a62", "#7b9a55"],
      wood: "#3e5a30", hedge: "rgba(42,60,30,.75)", tree: "rgba(34,52,26,.85)", road: "#cfc7ae", river: ["#4d6f7c", "#6d8f9a"], village: ["#9b5b48", "#bdb6a6"],
      zenLow: [66, 118, 186], zenHigh: [30, 64, 138], haze: [206, 218, 228], fog: [188, 200, 210], vis: 42000, ground: 1,
      clouds: { density: 0.36, base: 5200, depth: 900, lit: [255, 255, 258], shade: 0.82 } },
    italy: { label: "Po Valley, Italy", tex: "fields", tile: 9000,
      palette: ["#b49a63", "#c3a96c", "#9c9a5a", "#a88f55", "#8d9356", "#cbb27a", "#b7a26a", "#7f8a4c", "#d0b884"],
      wood: "#4f5f34", hedge: "rgba(80,70,40,.55)", tree: "rgba(60,70,36,.8)", road: "#e2d6b8", river: ["#6f8a86", "#8aa5a0"], village: ["#c08a64", "#e0d2b8"],
      zenLow: [82, 130, 192], zenHigh: [36, 70, 140], haze: [222, 216, 200], fog: [208, 202, 186], vis: 38000, ground: 1,
      clouds: { density: 0.14, base: 7000, depth: 700, lit: [255, 252, 246], shade: 0.86 } },
    channel: { label: "English Channel", tex: "sea", tile: 3000,
      zenLow: [70, 115, 175], zenHigh: [32, 62, 130], haze: [200, 212, 222], fog: [176, 192, 204], vis: 45000, ground: 1,
      clouds: { density: 0.45, base: 4200, depth: 900, lit: [250, 252, 255], shade: 0.78 } },
    pacific: { label: "Pacific atolls", tex: "islands", tile: 36000,
      zenLow: [40, 112, 202], zenHigh: [22, 60, 140], haze: [188, 220, 236], fog: [168, 204, 222], vis: 80000, ground: 1,
      clouds: { density: 0.3, base: 2600, depth: 1100, lit: [255, 255, 255], shade: 0.8 } },
    winter: { label: "Ardennes, winter 1944", tex: "fields", tile: 8000,
      palette: ["#e7ebee", "#dde3e8", "#f1f3f4", "#d4dbe1", "#e2e6e8", "#c9d1d6", "#eceff1"],
      wood: "#2f3a2e", hedge: "rgba(70,78,74,.6)", tree: "rgba(36,44,38,.9)", road: "#a9adab", river: ["#5f6f78", "#7a8a92"], village: ["#6d5a50", "#9a958e"],
      zenLow: [150, 160, 174], zenHigh: [96, 112, 138], haze: [204, 208, 212], fog: [206, 210, 214], vis: 24000, ground: 0.95,
      clouds: { density: 0.7, base: 3600, depth: 600, lit: [230, 232, 236], shade: 0.8 } },
    dusk: { label: "Dusk over England", tex: "fields", tile: 8000,
      palette: ["#6f9150", "#86a35a", "#9fa65f", "#668a47", "#b4a46a", "#5d7f40", "#91a85e", "#a99a62", "#7b9a55"],
      wood: "#3e5a30", hedge: "rgba(42,60,30,.75)", tree: "rgba(34,52,26,.85)", road: "#cfc7ae", river: ["#8a6f6a", "#c49b80"], village: ["#9b5b48", "#bdb6a6"],
      zenLow: [52, 62, 118], zenHigh: [22, 28, 70], haze: [240, 168, 112], fog: [150, 112, 104], vis: 36000, ground: 0.58,
      clouds: { density: 0.3, base: 5800, depth: 800, lit: [255, 186, 140], shade: 0.7 } }
  };
  let SC = SCENES.england;
  const MAC = 128, MAC_FT = 256000;    // regional brightness variation
  const SPAN_FT = 32.5;                // Bf 109 wingspan, dialled into the K-14
  const MUZZLE = 2870;                 // ft/s, .50 cal M2
  const CONVERGE = 900;                // guns converge at 300 yd

  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;

  let canvas, ctx, off, octx, oimg, obuf, D = 0, scaleK = 3, W = 0, H = 0, dpr = 1, F = 0, CY = 0;
  let mips = [], macro = null;
  const world = { x: 0, z: 0 };
  const prev = { pitch: 0, hdg: 270, ok: false };
  let rates = { q: 0, r: 0 };
  let groundTilt = 10;
  let shake = 0;

  const G = {
    rangeYd: 300, rounds: 1880, firing: false, lastSalvo: 0,
    bullets: [], hits: 0, kills: 0, target: null, respawnAt: 0, sparks: [], smoke: [], enabled: false
  };

  /* ---------- Terrain texture (tileable patchwork of English fields) ---------- */
  function genTexture() {
    const N = 16, C = TEX / N;
    const c = document.createElement("canvas"); c.width = c.height = TEX;
    const g = c.getContext("2d");
    const rnd = (i, j, s) => {
      i = ((i % N) + N) % N; j = ((j % N) + N) % N;
      let h = (i * 374761393 + j * 668265263 + s * 982451653) | 0;
      h = Math.imul(h ^ (h >>> 13), 1274126177);
      return ((h ^ (h >>> 16)) >>> 0) / 4294967295;
    };
    const P = (i, j) => [i * C + (rnd(i, j, 1) - 0.5) * C * 0.55, j * C + (rnd(i, j, 2) - 0.5) * C * 0.55];
    const palette = SC.palette || ["#6f9150"];
    g.fillStyle = palette[0]; g.fillRect(0, 0, TEX, TEX);
    if (SC.tex === "fields") {
    const quads = [];
    for (let i = -1; i <= N; i++) for (let j = -1; j <= N; j++) quads.push([i, j]);
    quads.forEach(([i, j]) => {
      const a = P(i, j), b = P(i + 1, j), cc = P(i + 1, j + 1), d = P(i, j + 1);
      g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.lineTo(cc[0], cc[1]); g.lineTo(d[0], d[1]); g.closePath();
      const wood = rnd(i, j, 3) < 0.1, village = !wood && rnd(i, j, 4) < 0.03;
      g.fillStyle = wood ? SC.wood : village ? SC.village[1] : palette[Math.floor(rnd(i, j, 5) * palette.length)];
      g.fill();
      g.save(); g.clip();
      if (wood) {
        for (let k = 0; k < 40; k++) { g.fillStyle = k % 2 ? "rgba(30,48,24,.6)" : "rgba(80,110,60,.35)"; g.beginPath(); g.arc(a[0] + rnd(i + k, j, 6) * C * 1.2, a[1] + rnd(i, j + k, 7) * C * 1.2, 1.5 + rnd(k, i, 8) * 2.5, 0, 7); g.fill(); }
      } else if (village) {
        for (let k = 0; k < 14; k++) { g.fillStyle = k % 3 ? SC.village[0] : SC.village[1]; g.fillRect(a[0] + rnd(i + k, j, 9) * C, a[1] + rnd(i, j + k, 10) * C, 2.5, 2); }
      } else if (rnd(i, j, 11) < 0.45) {
        const ang = rnd(i, j, 12) * Math.PI; g.strokeStyle = "rgba(40,40,20,.09)"; g.lineWidth = 1;
        for (let k = -C * 2; k < C * 2; k += 3) { g.beginPath(); g.moveTo(a[0] + Math.cos(ang) * -C * 2 + Math.sin(ang) * k, a[1] + Math.sin(ang) * -C * 2 - Math.cos(ang) * k); g.lineTo(a[0] + Math.cos(ang) * C * 2 + Math.sin(ang) * k, a[1] + Math.sin(ang) * C * 2 - Math.cos(ang) * k); g.stroke(); }
      }
      g.restore();
      // hedgerows
      g.strokeStyle = SC.hedge; g.lineWidth = 1.4; g.stroke();
    });
    // trees dotted along hedges
    for (let i = -1; i <= N; i++) for (let j = -1; j <= N; j++) {
      const a = P(i, j), b = P(i + 1, j);
      for (let k = 0; k < 4; k++) if (rnd(i, j, 20 + k) < 0.5) { const t = rnd(i, j, 30 + k); g.fillStyle = SC.tree; g.beginPath(); g.arc(lerp(a[0], b[0], t), lerp(a[1], b[1], t), 1.6, 0, 7); g.fill(); }
    }
    const line = (pts, color, w) => { g.strokeStyle = color; g.lineWidth = w; g.lineJoin = "round"; g.beginPath(); pts.forEach((p, k) => k ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.stroke(); };
    const road1 = [], road2 = [], river = [];
    for (let i = -1; i <= N + 1; i++) { road1.push(P(i, 5)); const p = P(i, 12), q = P(i, 13); river.push([p[0], (p[1] + q[1]) / 2]); }
    for (let j = -1; j <= N + 1; j++) road2.push(P(10, j));
    line(river, SC.river[0], 5); line(river, SC.river[1], 2.4);
    line(road1, SC.road, 2.2); line(road2, SC.road, 2.2);
    } else if (SC.tex === "sea") {
      g.fillStyle = "#2d5d78"; g.fillRect(0, 0, TEX, TEX);
      for (let k = 0; k < 90; k++) { const x = rnd(k, 1, 50) * TEX, y = rnd(k, 2, 51) * TEX, r = 30 + rnd(k, 3, 52) * 90;
        g.fillStyle = k % 2 ? "rgba(70,120,140,.18)" : "rgba(20,50,70,.2)"; for (const ox of [-TEX, 0, TEX]) for (const oy of [-TEX, 0, TEX]) { g.beginPath(); g.arc(x + ox, y + oy, r, 0, 7); g.fill(); } }
      g.strokeStyle = "rgba(235,242,245,.55)"; g.lineWidth = 1;
      for (let k = 0; k < 700; k++) { const x = rnd(k, 4, 53) * TEX, y = rnd(k, 5, 54) * TEX, l = 2 + rnd(k, 6, 55) * 4; g.beginPath(); g.moveTo(x, y); g.lineTo(x + l, y + l * 0.2); g.stroke(); }
    } else if (SC.tex === "islands") {
      g.fillStyle = "#17608a"; g.fillRect(0, 0, TEX, TEX);
      for (let k = 0; k < 60; k++) { const x = rnd(k, 1, 60) * TEX, y = rnd(k, 2, 61) * TEX, r = 40 + rnd(k, 3, 62) * 80;
        g.fillStyle = k % 2 ? "rgba(40,120,160,.18)" : "rgba(10,50,90,.2)"; for (const ox of [-TEX, 0, TEX]) for (const oy of [-TEX, 0, TEX]) { g.beginPath(); g.arc(x + ox, y + oy, r, 0, 7); g.fill(); } }
      const isles = [[120, 140, 34], [380, 330, 26], [300, 80, 14], [70, 420, 18], [450, 120, 10]];
      isles.forEach(([x, y, r]) => {
        g.fillStyle = "rgba(70,200,205,.55)"; g.beginPath(); g.ellipse(x, y, r * 1.9, r * 1.4, 0.4, 0, 7); g.fill();
        g.fillStyle = "#e9dcae"; g.beginPath(); g.ellipse(x, y, r * 1.25, r * 0.9, 0.4, 0, 7); g.fill();
        g.fillStyle = "#3f8a3e"; g.beginPath(); g.ellipse(x, y, r * 1.0, r * 0.68, 0.4, 0, 7); g.fill();
        g.fillStyle = "#58b8b8"; g.beginPath(); g.ellipse(x + r * 0.15, y, r * 0.55, r * 0.32, 0.4, 0, 7); g.fill();
      });
      g.strokeStyle = "rgba(235,245,248,.45)"; g.lineWidth = 1;
      for (let k = 0; k < 400; k++) { const x = rnd(k, 4, 63) * TEX, y = rnd(k, 5, 64) * TEX; g.beginPath(); g.moveTo(x, y); g.lineTo(x + 3, y + 0.6); g.stroke(); }
    }
    // speckle
    const id = g.getImageData(0, 0, TEX, TEX), px = id.data;
    for (let k = 0; k < px.length; k += 4) { const n = (Math.random() - 0.5) * 16; px[k] += n; px[k + 1] += n; px[k + 2] += n * 0.8; }
    g.putImageData(id, 0, 0);
    // mip chain
    mips = [];
    let src = c;
    for (let s = TEX; s >= 8; s >>= 1) {
      const m = document.createElement("canvas"); m.width = m.height = s;
      const mg = m.getContext("2d"); mg.imageSmoothingQuality = "high"; mg.drawImage(src, 0, 0, s, s);
      mips.push({ size: s, data: new Uint32Array(mg.getImageData(0, 0, s, s).data.buffer) });
      src = m;
    }
    // macro brightness: periodic value noise, two octaves
    macro = new Float32Array(MAC * MAC);
    const lat = (n, s) => { const a = new Float32Array(n * n); for (let k = 0; k < n * n; k++) a[k] = rnd(k % n, (k / n) | 0, s); return a; };
    const L1 = lat(8, 40), L2 = lat(16, 41);
    const sample = (L, n, x, y) => {
      const fx = x * n, fy = y * n, x0 = Math.floor(fx), y0 = Math.floor(fy), tx = fx - x0, ty = fy - y0;
      const sx = tx * tx * (3 - 2 * tx), sy = ty * ty * (3 - 2 * ty);
      const v = (i, j) => L[((j % n + n) % n) * n + ((i % n + n) % n)];
      return lerp(lerp(v(x0, y0), v(x0 + 1, y0), sx), lerp(v(x0, y0 + 1), v(x0 + 1, y0 + 1), sx), sy);
    };
    for (let y = 0; y < MAC; y++) for (let x = 0; x < MAC; x++) {
      const n = sample(L1, 8, x / MAC, y / MAC) * 0.7 + sample(L2, 16, x / MAC, y / MAC) * 0.3;
      macro[y * MAC + x] = 0.82 + n * 0.34;
    }
  }

  /* ---------- Sizing ---------- */
  function resize() {
    const r = canvas.getBoundingClientRect();
    dpr = Math.min(2, window.devicePixelRatio || 1);
    W = Math.max(200, r.width); H = Math.max(120, r.height);
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    F = (W / 2) / Math.tan(31 * DEG);          // ~62° horizontal field of view
    CY = H * 0.42;                             // boresight sits above the nose, so more ground shows below
    const diag = 2 * Math.hypot(W / 2, Math.max(CY, H - CY));
    scaleK = Math.max(2, diag / 420);
    D = Math.ceil(diag / scaleK);
    off.width = off.height = D;
    oimg = octx.createImageData(D, D);
    obuf = new Uint32Array(oimg.data.buffer);
  }

  /* ---------- Ground + sky ---------- */
  function renderGround(S, pitchDeg) {
    const half = D / 2, Fo = F / scaleK;
    const eye = Math.max(S.alt, 0) + 9;
    const p = pitchDeg * DEG, cp = Math.cos(p), sp = Math.sin(p);
    const h = S.hdg * DEG, sh = Math.sin(h), ch = Math.cos(h);
    const altF = clamp(S.alt / 30000, 0, 1);
    const zen = [0, 1, 2].map(i => lerp(SC.zenLow[i], SC.zenHigh[i], altF));
    const haze = SC.haze, fogC = SC.fog;
    const vis = SC.vis * (1 + Math.max(S.alt, 0) / 5000);
    const gm = SC.ground;
    const sea = SC.tex !== "fields";
    const maxLvl = mips.length - 1, texel0 = TILE_FT / TEX;
    const lowAlt = S.alt < 3000;
    for (let y = 0; y < D; y++) {
      const u = -(y + 0.5 - half) / Fo;
      const uW = u * cp + sp, fW = cp - u * sp;
      const row = y * D;
      const nrm = Math.hypot(uW, fW, 0.0001);
      if (uW >= -0.0004) {
        const e = clamp(uW / nrm, 0, 1), t = clamp(e / 0.55, 0, 1), s = t * t * (3 - 2 * t);
        const col = 0xff000000 | (Math.round(lerp(haze[2], zen[2], s)) << 16) | (Math.round(lerp(haze[1], zen[1], s)) << 8) | Math.round(lerp(haze[0], zen[0], s));
        obuf.fill(col, row, row + D);
        continue;
      }
      const t = Math.min(eye / -uW, 400000);
      const fwd = fW * t;
      const dR = t / Fo;
      const dist = Math.abs(t * nrm), far = clamp((dist - 120000) / 220000, 0, 1);
      const fog = Math.max(clamp(1 - Math.exp(-Math.pow(dist / vis, 1.35)), 0, 0.97), far * far * (3 - 2 * far));
      if (fog > 0.985) { obuf.fill(0xff000000 | (fogC[2] << 16) | (fogC[1] << 8) | fogC[0], row, row + D); continue; }
      const fpv = dR / Math.max(0.03, -uW / nrm);
      const lvl = clamp(Math.floor(Math.log2(Math.sqrt(dR * fpv) / texel0) + 1), 0, maxLvl);
      const m = mips[lvl], size = m.size, data = m.data, mask = size - 1, k = size / TILE_FT;
      const inv = 1 - fog, fr = fogC[0] * fog, fg = fogC[1] * fog, fb = fogC[2] * fog;
      const right0 = (0.5 - half) * dR;
      let X = world.x + fwd * sh + right0 * ch, Z = world.z + fwd * ch - right0 * sh;
      const dX = dR * ch, dZ = -dR * sh;
      const mk = MAC / MAC_FT;
      for (let x = 0; x < D; x++, X += dX, Z += dZ) {
        let c = data[((((Z * k) | 0) & mask) * size) + (((X * k) | 0) & mask)];
        let r = c & 255, g = (c >> 8) & 255, b = (c >> 16) & 255;
        if (sea && lowAlt && Z > -700 && Z < 700 && X < 1400 && X > -7400) { r = 112; g = 134; b = 84; }
        if (lowAlt && Z > -80 && Z < 80 && X < 600 && X > -6600) {
          const center = Z > -3 && Z < 3 && ((X | 0) >> 6) & 1;
          r = g = b = center ? 225 : 104; b = center ? 220 : 100;
        }
        // regional variation (bilinear)
        const mx = X * mk, mz = Z * mk, x0 = Math.floor(mx), z0 = Math.floor(mz), tx = mx - x0, tz = mz - z0;
        const i0 = x0 & (MAC - 1), i1 = (x0 + 1) & (MAC - 1), j0 = (z0 & (MAC - 1)) * MAC, j1 = ((z0 + 1) & (MAC - 1)) * MAC;
        const mv = (macro[j0 + i0] * (1 - tx) + macro[j0 + i1] * tx) * (1 - tz) + (macro[j1 + i0] * (1 - tx) + macro[j1 + i1] * tx) * tz;
        const mi = (sea ? 0.55 + mv * 0.45 : mv) * inv * gm;
        r = r * mi + fr; g = g * mi + fg; b = b * mi + fb;
        obuf[row + x] = 0xff000000 | ((b > 255 ? 255 : b) << 16) | ((g > 255 ? 255 : g) << 8) | (r > 255 ? 255 : r);
      }
    }
    octx.putImageData(oimg, 0, 0);
  }

  /* ---------- 3D projection (camera frame, before bank) ---------- */
  let cam = null;
  function setCam(S, pitchDeg) {
    const p = pitchDeg * DEG, h = S.hdg * DEG;
    cam = { cp: Math.cos(p), sp: Math.sin(p), ch: Math.cos(h), sh: Math.sin(h), eye: Math.max(S.alt, 0) + 9 };
  }
  function project(x, y, z) {
    const dx = x - world.x, dz = z - world.z, dy = y - cam.eye;
    const f = dx * cam.sh + dz * cam.ch, r = dx * cam.ch - dz * cam.sh;
    const fc = f * cam.cp + dy * cam.sp, uc = dy * cam.cp - f * cam.sp;
    if (fc < 3) return null;
    return { x: (F * r) / fc, y: (-F * uc) / fc, d: fc };
  }

  /* ---------- Clouds ---------- */
  function hash(i, j, s) { let h = (i * 73856093) ^ (j * 19349663) ^ (s * 83492791); h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967295; }
  function drawClouds(S) {
    const CELL = 5200, R = 13;
    const ci = Math.floor(world.x / CELL), cj = Math.floor(world.z / CELL);
    const list = [];
    const haze = SC.haze, CL = SC.clouds;
    const vis = SC.vis * 1.4 * (1 + Math.max(S.alt, 0) / 6000);
    for (let i = ci - R; i <= ci + R; i++) for (let j = cj - R; j <= cj + R; j++) {
      if (hash(i, j, 1) > CL.density) continue;
      const cx = (i + hash(i, j, 2)) * CELL, cz = (j + hash(i, j, 3)) * CELL, cy = CL.base + hash(i, j, 4) * CL.depth;
      const size = 900 + hash(i, j, 5) * 1700;
      const pc = project(cx, cy, cz);
      if (!pc || pc.d > 75000) continue;
      const marg = (F * size * 1.4) / pc.d;
      if (Math.abs(pc.x) > W * 0.8 + marg || Math.abs(pc.y) > H * 0.9 + marg) continue;
      list.push({ i, j, cx, cy, cz, size, d: pc.d });
    }
    list.sort((a, b) => b.d - a.d);
    list.forEach(c => {
      const fog = clamp(1 - Math.exp(-c.d / vis), 0, 1);
      const near = clamp((c.d - 150) / 1400, 0, 1);
      for (let k = 0; k < 6; k++) {
        const ox = (hash(c.i, c.j, 10 + k) - 0.5) * c.size * 1.3, oz = (hash(c.i, c.j, 20 + k) - 0.5) * c.size * 0.9;
        const oy = (k === 0 ? 0 : hash(c.i, c.j, 30 + k) * c.size * 0.35);
        const rad = c.size * (0.38 + hash(c.i, c.j, 40 + k) * 0.25);
        const p = project(c.cx + ox, c.cy + oy, c.cz + oz);
        if (!p) continue;
        const rp = (F * rad) / p.d;
        if (rp < 0.7) continue;
        const shade = CL.shade + (oy / (c.size * 0.35 + 1)) * (1 - CL.shade);
        const r = lerp(CL.lit[0] * shade, haze[0], fog), g = lerp(CL.lit[1] * shade, haze[1], fog), b = lerp(CL.lit[2] * shade, haze[2], fog);
        const grad = ctx.createRadialGradient(p.x, p.y - rp * 0.2, rp * 0.1, p.x, p.y, rp);
        grad.addColorStop(0, `rgba(${r | 0},${g | 0},${Math.min(255, b) | 0},${0.95 * near})`);
        grad.addColorStop(0.7, `rgba(${r | 0},${g | 0},${Math.min(255, b) | 0},${0.75 * near})`);
        grad.addColorStop(1, `rgba(${r | 0},${g | 0},${Math.min(255, b) | 0},0)`);
        ctx.fillStyle = grad;
        ctx.beginPath(); ctx.arc(p.x, p.y, rp, 0, Math.PI * 2); ctx.fill();
      }
    });
  }

  /* ---------- Practice target ---------- */
  function ownVectors(S) {
    const h = S.hdg * DEG, g = S.pitch * DEG, b = S.bank * DEG;
    const n = [Math.sin(h) * Math.cos(g), Math.sin(g), Math.cos(h) * Math.cos(g)];
    const r0 = [Math.cos(h), 0, -Math.sin(h)];
    const u0 = [-Math.sin(h) * Math.sin(g), Math.cos(g), -Math.cos(h) * Math.sin(g)];
    const right = r0.map((v, i) => v * Math.cos(b) - u0[i] * Math.sin(b));
    const up = u0.map((v, i) => v * Math.cos(b) + r0[i] * Math.sin(b));
    return { n, right, up };
  }
  function spawnTarget(S) {
    const { n, right } = ownVectors(S);
    const dist = 1100 + Math.random() * 500;
    const side = (Math.random() - 0.5) * 260;
    G.target = {
      x: world.x + n[0] * dist + right[0] * side, y: Math.max(1500, S.alt + 60 + (Math.random() - 0.5) * 120), z: world.z + n[2] * dist + right[2] * side,
      hdg: S.hdg + (Math.random() - 0.5) * 20, pitch: 0, bank: 0, spd: Math.max(330, S.tas - 18) * FTS, t: 0, phase: Math.random() * 6,
      hp: 32, state: "fly", downAt: 0, roll: 0
    };
  }
  function updateTarget(S, dt, now) {
    const T = G.target;
    if (!T) { if (G.enabled && G.respawnAt && now > G.respawnAt && !S.onGround) { G.respawnAt = 0; spawnTarget(S); } return; }
    T.t += dt;
    if (T.state === "down") {
      T.roll += 140 * dt; T.pitch = Math.max(-55, T.pitch - 18 * dt); T.spd = Math.min(T.spd + 30 * dt, 700);
    } else {
      const weave = (T.state === "smoke" ? 5 : 9) * Math.sin(T.t * 0.33 + T.phase) + 3 * Math.sin(T.t * 0.9 + T.phase * 2);
      T.hdg += weave * dt;
      T.bank = Math.atan((weave * DEG * T.spd) / 32.2) / DEG;
      T.pitch = 3 * Math.sin(T.t * 0.25 + T.phase);
      if (T.y < 1200) T.pitch = 8;
      const target = Math.max(300, S.tas - (T.state === "smoke" ? 35 : 14)) * FTS;
      T.spd = lerp(T.spd, target, 1 - Math.exp(-0.4 * dt));
    }
    const h = T.hdg * DEG, g = T.pitch * DEG;
    T.x += Math.sin(h) * Math.cos(g) * T.spd * dt; T.y += Math.sin(g) * T.spd * dt; T.z += Math.cos(h) * Math.cos(g) * T.spd * dt;
    if (T.state !== "fly") {
      G.smoke.push({ x: T.x, y: T.y, z: T.z, born: now, dark: T.state === "down" });
      if (G.smoke.length > 220) G.smoke.splice(0, G.smoke.length - 220);
    }
    const p = project(T.x, T.y, T.z);
    const dist = Math.hypot(T.x - world.x, T.y - (S.alt + 9), T.z - world.z);
    if (T.state === "down" && (now - T.downAt > 7000 || T.y < 50)) { G.target = null; G.respawnAt = now + 2500; return; }
    if (T.state !== "down" && (dist > 9000 || (!p && dist > 400))) { spawnTarget(S); }
  }
  function drawTarget(S) {
    const T = G.target; if (!T) return;
    const fog = clamp(1 - Math.exp(-Math.hypot(T.x - world.x, T.z - world.z) / (70000 + S.alt * 2)), 0, 1);
    const h = T.hdg * DEG, pt = T.pitch * DEG, b = (T.bank + T.roll) * DEG;
    const cb = Math.cos(b), sb = Math.sin(b), cpp = Math.cos(pt), spp = Math.sin(pt), chh = Math.cos(h), shh = Math.sin(h);
    const L = (lx, ly, lz) => {
      const x1 = lx * cb + ly * sb, y1 = -lx * sb + ly * cb, z1 = lz;
      const y2 = y1 * cpp + z1 * spp, z2 = z1 * cpp - y1 * spp;
      return project(T.x + x1 * chh + z2 * shh, T.y + y2, T.z - x1 * shh + z2 * chh);
    };
    const center = project(T.x, T.y, T.z);
    if (!center) return;
    const body = `rgb(${lerp(62, 200, fog) | 0},${lerp(70, 212, fog) | 0},${lerp(60, 222, fog) | 0})`;
    const poly = pts => { const q = pts.map(p => L(...p)); if (q.some(v => !v)) return; ctx.beginPath(); q.forEach((v, k) => k ? ctx.lineTo(v.x, v.y) : ctx.moveTo(v.x, v.y)); ctx.closePath(); ctx.fill(); };
    ctx.fillStyle = body; ctx.strokeStyle = body; ctx.lineCap = "round";
    poly([[-16.2, 0, 1.5], [-2, -0.6, 5.5], [2, -0.6, 5.5], [16.2, 0, 1.5], [16.2, 0, -1.2], [2, -0.6, -2.5], [-2, -0.6, -2.5], [-16.2, 0, -1.2]]);
    poly([[-5.5, 0.4, -12.5], [0, 0.4, -11], [5.5, 0.4, -12.5], [5.5, 0.4, -14.2], [-5.5, 0.4, -14.2]]);
    poly([[0, 0.5, -11.5], [0, 6.2, -13.8], [0, 6.2, -15], [0, 0.5, -15]]);
    const nose = L(0, 0, 14.5), tail = L(0, 0.4, -14.5);
    if (nose && tail) {
      ctx.lineWidth = Math.max(1.2, (F * 3.1) / center.d);
      ctx.beginPath(); ctx.moveTo(nose.x, nose.y); ctx.lineTo(tail.x, tail.y); ctx.stroke();
      const canopy = L(0, 1.6, 2);
      if (canopy) { ctx.lineWidth = Math.max(0.8, (F * 1.6) / center.d); ctx.beginPath(); ctx.moveTo(canopy.x, canopy.y); const c2 = L(0, 1.2, -3); c2 && ctx.lineTo(c2.x, c2.y); ctx.stroke(); }
      ctx.fillStyle = `rgba(242,194,48,${1 - fog})`;
      ctx.beginPath(); ctx.arc(nose.x, nose.y, Math.max(0.8, (F * 1.4) / center.d), 0, 7); ctx.fill();
    }
    if ((F * SPAN_FT) / center.d < 4) { ctx.fillStyle = body; ctx.beginPath(); ctx.arc(center.x, center.y, 1.6, 0, 7); ctx.fill(); }
  }
  function drawSmoke(now) {
    G.smoke = G.smoke.filter(s => now - s.born < 4500);
    for (let i = 0; i < G.smoke.length; i++) {
      const s = G.smoke[i], age = (now - s.born) / 4500;
      const p = project(s.x, s.y + age * 40, s.z); if (!p) continue;
      const r = (F * (6 + age * 40)) / p.d;
      ctx.fillStyle = s.dark ? `rgba(40,38,36,${0.55 * (1 - age)})` : `rgba(120,120,118,${0.4 * (1 - age)})`;
      ctx.beginPath(); ctx.arc(p.x, p.y, Math.max(0.6, r), 0, 7); ctx.fill();
    }
  }

  /* ---------- Guns ---------- */
  function fire(S, now) {
    if (!G.enabled || !G.firing || G.rounds <= 0 || S.onGround) return;
    if (now - G.lastSalvo < 77) return;               // ~13 salvos/s from six guns
    G.lastSalvo = now;
    G.rounds = Math.max(0, G.rounds - 6);
    const { n, right, up } = ownVectors(S);
    const v = S.tas * FTS;
    [-1, 1].forEach(side => {
      const o = [right[0] * 10.5 * side - up[0] * 2, right[1] * 10.5 * side - up[1] * 2, right[2] * 10.5 * side - up[2] * 2];
      // aim each wing's guns at the convergence point
      const aim = [n[0] * CONVERGE - o[0], n[1] * CONVERGE - o[1], n[2] * CONVERGE - o[2]];
      const al = Math.hypot(...aim);
      const j = () => (Math.random() - 0.5) * 0.004;
      const dir = [aim[0] / al + j(), aim[1] / al + j(), aim[2] / al + j()];
      G.bullets.push({
        x: world.x + o[0], y: S.alt + 9 + o[1], z: world.z + o[2],
        vx: n[0] * v + dir[0] * MUZZLE, vy: n[1] * v + dir[1] * MUZZLE, vz: n[2] * v + dir[2] * MUZZLE,
        born: now, px: null, tracer: Math.random() < 0.55
      });
    });
    shake = 1;
    window.EngineAudio && window.EngineAudio.gun && window.EngineAudio.gun();
  }
  function updateBullets(dt, now) {
    const T = G.target;
    G.bullets = G.bullets.filter(b => now - b.born < 1400);
    G.bullets.forEach(b => {
      b.px = b.x; b.py = b.y; b.pz = b.z;
      b.vy -= 32.2 * dt;
      b.x += b.vx * dt; b.y += b.vy * dt; b.z += b.vz * dt;
      if (T && T.state !== "down" && !b.hit) {
        // segment-to-point distance
        const sx = b.x - b.px, sy = b.y - b.py, sz = b.z - b.pz;
        const wx = T.x - b.px, wy = T.y - b.py, wz = T.z - b.pz;
        const tt = clamp((wx * sx + wy * sy + wz * sz) / (sx * sx + sy * sy + sz * sz || 1), 0, 1);
        const d = Math.hypot(wx - sx * tt, wy - sy * tt, wz - sz * tt);
        if (d < 17) {
          b.hit = true; G.hits++; T.hp -= 1;
          G.sparks.push({ x: T.x, y: T.y, z: T.z, born: now });
          if (T.hp <= 14 && T.state === "fly") T.state = "smoke";
          if (T.hp <= 0) { T.state = "down"; T.downAt = now; G.kills++; }
        }
      }
    });
  }
  function drawBullets(now) {
    ctx.lineCap = "round";
    G.bullets.forEach(b => {
      if (!b.tracer || b.px === null || b.hit) return;
      const a = project(b.x, b.y, b.z), p = project(b.px, b.py, b.pz);
      if (!a || !p) return;
      const age = (now - b.born) / 1400;
      ctx.strokeStyle = `rgba(255,${200 - age * 80 | 0},90,${0.95 - age * 0.6})`;
      ctx.lineWidth = Math.max(1, 3.2 - age * 2.4);
      ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(a.x, a.y); ctx.stroke();
    });
    G.sparks = G.sparks.filter(s => now - s.born < 220);
    G.sparks.forEach(s => {
      const p = project(s.x, s.y, s.z); if (!p) return;
      const r = Math.max(3, (F * 9) / p.d) * (1 + (now - s.born) / 220);
      ctx.fillStyle = `rgba(255,236,170,${1 - (now - s.born) / 220})`;
      ctx.beginPath(); ctx.arc(p.x + (Math.random() - 0.5) * r, p.y + (Math.random() - 0.5) * r, r * 0.45, 0, 7); ctx.fill();
    });
  }

  /* ---------- Cockpit frame + K-14 sight (fixed to the aircraft) ---------- */
  function drawFrame(S) {
    // anti-glare nose
    ctx.fillStyle = "#2c3223";
    ctx.beginPath();
    const bot = H - CY + 2, top = -CY - 2, nose = H - CY - H * 0.2;
    ctx.moveTo(-W * 0.62, bot); ctx.lineTo(-W * 0.62, nose);
    ctx.quadraticCurveTo(-W * 0.2, nose + H * 0.03, 0, nose + H * 0.035);
    ctx.quadraticCurveTo(W * 0.2, nose + H * 0.03, W * 0.62, nose);
    ctx.lineTo(W * 0.62, bot); ctx.closePath(); ctx.fill();
    ctx.fillStyle = "rgba(255,255,255,.05)";
    ctx.fillRect(-W * 0.62, nose, W * 1.24, 2);
    // windscreen posts
    ctx.fillStyle = "#23281c";
    [-1, 1].forEach(s => {
      ctx.beginPath();
      ctx.moveTo(s * W * 0.255, bot); ctx.lineTo(s * W * 0.285, bot);
      ctx.lineTo(s * W * 0.22, top); ctx.lineTo(s * W * 0.19, top); ctx.closePath(); ctx.fill();
    });
    // combining glass
    const gw = Math.min(W * 0.2, 190), gh = gw * 0.8;
    ctx.fillStyle = "rgba(170,205,195,.06)"; ctx.strokeStyle = "rgba(255,255,255,.16)"; ctx.lineWidth = 1.2;
    ctx.beginPath(); ctx.rect(-gw / 2, -gh * 0.62, gw, gh); ctx.fill(); ctx.stroke();
    ctx.fillStyle = "#1b1f17"; ctx.fillRect(-gw * 0.36, nose - H * 0.01, gw * 0.72, H * 0.06);
  }
  function drawSight(S) {
    const tof = (G.rangeYd * 3) / (MUZZLE * 0.92);
    let lx = -rates.r * tof * F, ly = rates.q * tof * F;
    const lim = Math.min(W, H) * 0.32;
    lx = clamp(lx, -lim, lim); ly = clamp(ly, -lim, lim);
    const rad = Math.max(10, ((F * SPAN_FT) / (G.rangeYd * 3)) / 2);
    ctx.save();
    ctx.shadowColor = "rgba(255,150,60,.9)"; ctx.shadowBlur = 6;
    // fixed cross
    ctx.strokeStyle = "rgba(255,190,110,.55)"; ctx.lineWidth = 1.2;
    ctx.beginPath(); ctx.moveTo(-9, 0); ctx.lineTo(-3, 0); ctx.moveTo(3, 0); ctx.lineTo(9, 0); ctx.moveTo(0, -9); ctx.lineTo(0, -3); ctx.moveTo(0, 3); ctx.lineTo(0, 9); ctx.stroke();
    // gyro reticle: six diamonds + centre pip
    ctx.fillStyle = "rgba(255,176,70,.95)";
    for (let k = 0; k < 6; k++) {
      const a = (k / 6) * Math.PI * 2 + Math.PI / 6;
      const x = lx + Math.cos(a) * rad, y = ly + Math.sin(a) * rad;
      ctx.beginPath(); ctx.moveTo(x, y - 4); ctx.lineTo(x + 3, y); ctx.lineTo(x, y + 4); ctx.lineTo(x - 3, y); ctx.closePath(); ctx.fill();
    }
    ctx.beginPath(); ctx.arc(lx, ly, 1.8, 0, 7); ctx.fill();
    ctx.restore();
    return { lx, ly, rad };
  }
  function drawOffscreenCue(S) {
    const T = G.target; if (!T || T.state === "down") return;
    const p = project(T.x, T.y, T.z);
    let x, y;
    const b = -S.bank * DEG;
    if (p) { x = p.x * Math.cos(b) - p.y * Math.sin(b); y = p.x * Math.sin(b) + p.y * Math.cos(b); if (Math.abs(x) < W / 2 - 20 && y > -CY + 20 && y < H - CY - 20) return; }
    else {
      const dx = T.x - world.x, dz = T.z - world.z;
      const r = dx * cam.ch - dz * cam.sh; x = r >= 0 ? 1 : -1; y = 0.2;
    }
    const a = Math.atan2(y, x), ex = Math.cos(a) * (W / 2 - 28), ey = Math.sin(a) * (H / 2 - 28);
    ctx.save(); ctx.translate(clamp(ex, -W / 2 + 28, W / 2 - 28), clamp(ey, -CY + 28, H - CY - H * 0.22)); ctx.rotate(a);
    ctx.fillStyle = "rgba(255,176,70,.9)"; ctx.beginPath(); ctx.moveTo(12, 0); ctx.lineTo(-6, -8); ctx.lineTo(-2, 0); ctx.lineTo(-6, 8); ctx.closePath(); ctx.fill();
    ctx.restore();
  }

  /* ---------- Frame ---------- */
  let hudEls = null, lastHud = 0, lastGist = "", lastSaid = 0;
  function frame(dt, S, now) {
    if (!canvas || !D) return;
    // own position (real time, flight path along the nose)
    const v = S.tas * FTS, h = S.hdg * DEG, g = S.pitch * DEG;
    world.x += Math.sin(h) * Math.cos(g) * v * dt;
    world.z += Math.cos(h) * Math.cos(g) * v * dt;
    // angular rates for the gyro sight (rad/s), in the aircraft frame
    if (prev.ok && dt > 0) {
      const dp = (S.pitch - prev.pitch) * DEG / dt;
      let dh = S.hdg - prev.hdg; if (dh > 180) dh -= 360; if (dh < -180) dh += 360;
      const w = (dh * DEG) / dt, b = S.bank * DEG;
      const q = dp + w * Math.sin(b), r = w * Math.cos(b);
      rates.q = lerp(rates.q, q, 1 - Math.exp(-6 * dt));
      rates.r = lerp(rates.r, r, 1 - Math.exp(-6 * dt));
    }
    prev.pitch = S.pitch; prev.hdg = S.hdg; prev.ok = true;
    // tail-down attitude on the ground: you can't see over the nose until the tail lifts
    const tiltTarget = S.onGround ? 10 * clamp(1 - (S.ias - 45) / 45, 0, 1) : 0;
    groundTilt = lerp(groundTilt, tiltTarget, 1 - Math.exp(-3 * dt));
    const camPitch = S.pitch + groundTilt;

    if (G.enabled && !G.target && !G.respawnAt && !S.onGround) spawnTarget(S);
    setCam(S, camPitch);
    updateTarget(S, dt, now);
    fire(S, now);
    updateBullets(dt, now);

    renderGround(S, camPitch);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    const calm = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const jx = shake && !calm ? (Math.random() - 0.5) * 1.6 : 0, jy = shake && !calm ? (Math.random() - 0.5) * 1.6 : 0;
    shake = 0;
    const engineBuzz = S.engineOn && !calm ? (Math.random() - 0.5) * 0.5 * (S.rpm / 3000) : 0;
    ctx.translate(W / 2 + jx, CY + jy + engineBuzz);
    ctx.save();
    ctx.rotate(-S.bank * DEG);
    ctx.imageSmoothingEnabled = true;
    const diag = D * scaleK;
    ctx.drawImage(off, -diag / 2, -diag / 2, diag, diag);
    drawClouds(S);
    drawSmoke(now);
    drawTarget(S);
    drawBullets(now);
    ctx.restore();
    // Propeller disc shimmer when the engine runs
    drawFrame(S);
    drawSight(S);
    drawOffscreenCue(S);

    if (now - lastHud > 120) {
      lastHud = now;
      hudEls.rounds.textContent = G.rounds.toLocaleString("en-US");
      hudEls.hits.textContent = G.hits;
      hudEls.kills.textContent = G.kills;
      hudEls.range.textContent = G.rangeYd + " yd";
      let msg;
      if (S.onGround && !S.engineOn) msg = "Tail down on the ground: the long nose hides the runway, which is why Mustang pilots taxied in S-turns. Start the engine, or use Air start.";
      else if (S.onGround) msg = "Open the throttle. The tail comes up around 60 mph and the runway appears over the nose.";
      else if (!G.enabled) msg = "Drag on the view (or the stick) to fly. Turn on gunnery practice to put a target ahead of you.";
      else if (G.rounds <= 0) msg = "Out of ammunition: 1,880 rounds goes in about 23 seconds. Reset gunnery to rearm.";
      else if (G.target && G.target.state === "down") msg = "Target destroyed. Another will appear shortly.";
      else if (G.target) {
        const d = Math.hypot(G.target.x - world.x, G.target.y - S.alt, G.target.z - world.z) / 3;
        const span = (F * SPAN_FT) / (d * 3), ring = (F * SPAN_FT) / (G.rangeYd * 3);
        const ratio = span / ring;
        msg = d > 900 ? `Target at about ${Math.round(d / 10) * 10} yd. Close to under 400 yd before firing.`
          : Math.abs(ratio - 1) < 0.2 ? "Range set: the wings fill the diamonds. Put the centre pip on the target and hold Fire."
          : ratio > 1 ? "The target looks bigger than the diamonds: it's closer than the range you've set. Turn the range down."
          : "The target looks smaller than the diamonds: it's further than the range you've set. Turn the range up, or close in.";
      } else msg = "Looking for the target...";
      if (hudEls.msg.textContent !== msg) hudEls.msg.textContent = msg;
      // announce to screen readers only on meaningful changes, at most every 3 s, without changing numbers
      const gist = msg.replace(/\d[\d,]*/g, "#");
      if (gist !== lastGist && now - lastSaid > 3000) { lastGist = gist; lastSaid = now; hudEls.live.textContent = msg; }
    }
  }

  /* ---------- Input ---------- */
  function bind() {
    const C = window.Cockpit;
    let drag = null;
    canvas.addEventListener("pointerdown", e => {
      if (e.button !== 0) return;
      canvas.setPointerCapture(e.pointerId);
      drag = { x: e.clientX, y: e.clientY };
      C.setStick(0, 0, true);
      canvas.focus({ preventScroll: true });
    });
    canvas.addEventListener("pointermove", e => {
      if (!drag) return;
      if (e.pointerType === "mouse" && !(e.buttons & 1)) { end(); return; }
      const s = Math.min(W, H) * 0.32;
      let x = (e.clientX - drag.x) / s, y = (e.clientY - drag.y) / s;
      const m = Math.hypot(x, y); if (m > 1) { x /= m; y /= m; }
      C.setStick(x, y, true);
    });
    const end = () => { drag = null; C.setStick(null, null, false); };
    canvas.addEventListener("pointerup", end); canvas.addEventListener("pointercancel", end); canvas.addEventListener("lostpointercapture", end);
    canvas.addEventListener("contextmenu", e => e.preventDefault());
    canvas.addEventListener("wheel", e => { if (!G.enabled) return; e.preventDefault(); setRange(G.rangeYd + (e.deltaY > 0 ? 25 : -25)); }, { passive: false });

    const keyTarget = el => el && (el === canvas || el.id === "stickPad");
    const isFire = e => e.code === "Space" || e.code === "KeyF";
    document.addEventListener("keydown", e => {
      if (!keyTarget(document.activeElement)) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      if (isFire(e)) { e.preventDefault(); if (G.enabled) G.firing = true; }
      if (e.key === "[") setRange(G.rangeYd - 25);
      if (e.key === "]") setRange(G.rangeYd + 25);
      if (document.activeElement === canvas) C.key(e, true);
    });
    document.addEventListener("keyup", e => {
      if (isFire(e) || e.key === "Meta") G.firing = false;
      C.key(e, false);
    });
    // releasing focus mid-press must not leave guns or stick keys held down
    const releaseKeys = () => { G.firing = false; ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].forEach(k => C.key({ key: k, preventDefault() {} }, false)); };
    canvas.addEventListener("blur", releaseKeys);
    window.addEventListener("blur", releaseKeys);
    document.getElementById("stickPad").addEventListener("blur", () => { G.firing = false; });

    const fireBtn = document.getElementById("fireBtn");
    const fdown = e => { if (e.button !== 0) return; e.preventDefault(); G.firing = true; fireBtn.setPointerCapture && e.pointerId !== undefined && fireBtn.setPointerCapture(e.pointerId); };
    const fup = () => { G.firing = false; };
    fireBtn.addEventListener("pointerdown", fdown);
    fireBtn.addEventListener("pointerup", fup); fireBtn.addEventListener("pointercancel", fup); fireBtn.addEventListener("pointerleave", fup);
    fireBtn.addEventListener("keydown", e => { if ((e.key === " " || e.key === "Enter")) { e.preventDefault(); G.firing = true; } });
    fireBtn.addEventListener("keyup", fup); fireBtn.addEventListener("blur", fup); fireBtn.addEventListener("lostpointercapture", fup);

    document.getElementById("rangeDown").addEventListener("click", () => setRange(G.rangeYd - 25));
    document.getElementById("rangeUp").addEventListener("click", () => setRange(G.rangeYd + 25));
    const gun = document.getElementById("gunneryToggle");
    gun.addEventListener("click", () => setGunnery(!G.enabled));
    document.getElementById("airStart").addEventListener("click", () => { C.airStart(); world.x = 0; world.z = 60000; prev.ok = false; groundTilt = 0; rates.q = rates.r = 0; });
    const sel = document.getElementById("sceneSel");
    sel.innerHTML = Object.keys(SCENES).map(k => `<option value="${k}">${SCENES[k].label}</option>`).join("");
    let saved = null; try { saved = localStorage.getItem("scene"); } catch (e) { /* ignore */ }
    if (saved && SCENES[saved] && saved !== "england") { sel.value = saved; setScene(saved); }
    sel.addEventListener("change", () => { setScene(sel.value); try { localStorage.setItem("scene", sel.value); } catch (e) { /* ignore */ } });
  }
  function setScene(k) { SC = SCENES[k] || SCENES.england; TILE_FT = SC.tile; genTexture(); }
  function setRange(v) { G.rangeYd = clamp(Math.round(v / 25) * 25, 200, 800); }
  function setGunnery(on) {
    G.enabled = on;
    const gun = document.getElementById("gunneryToggle");
    gun.setAttribute("aria-pressed", String(on));
    gun.textContent = on ? "End gunnery practice" : "Start gunnery practice";
    document.getElementById("viewRoot").classList.toggle("gunnery", on);
    if (on) { G.rounds = 1880; G.hits = 0; G.kills = 0; G.target = null; G.respawnAt = 0; window.Cockpit.setTime(1); }
    else { G.target = null; G.bullets = []; G.smoke = []; G.firing = false; }
  }
  function reset() { world.x = 0; world.z = 0; groundTilt = 10; prev.ok = false; setGunnery(false); }

  function init() {
    canvas = document.getElementById("viewCanvas");
    if (!canvas) return;
    ctx = canvas.getContext("2d");
    off = document.createElement("canvas"); octx = off.getContext("2d", { willReadFrequently: true });
    hudEls = { rounds: document.getElementById("hudRounds"), hits: document.getElementById("hudHits"), kills: document.getElementById("hudKills"), range: document.getElementById("hudRange"), msg: document.getElementById("viewMsg"), live: document.getElementById("viewLive") };
    genTexture();
    resize();
    new ResizeObserver(resize).observe(canvas);
    bind();
  }

  window.FlightView = { init, frame, reset };
})();
