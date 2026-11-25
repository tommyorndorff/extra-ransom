/* SVG instrument builders. Angles are degrees clockwise from 12 o'clock. */
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const C = 100;
  const pt = (a, r) => { const t = (a * Math.PI) / 180; return [C + r * Math.sin(t), C - r * Math.cos(t)]; };
  const el = (name, attrs, parent) => {
    const n = document.createElementNS(NS, name);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  };
  const arcPath = (a0, a1, r) => {
    const [x0, y0] = pt(a0, r), [x1, y1] = pt(a1, r);
    const large = Math.abs(a1 - a0) > 180 ? 1 : 0;
    return `M${x0} ${y0} A${r} ${r} 0 ${large} 1 ${x1} ${y1}`;
  };
  function base(svg) {
    el("circle", { cx: C, cy: C, r: 97, class: "bezel" }, svg);
    el("circle", { cx: C, cy: C, r: 90, class: "face" }, svg);
    // Screw heads for a touch of realism
    [45, 135, 225, 315].forEach(a => { const [x, y] = pt(a, 93.5); el("circle", { cx: x, cy: y, r: 2.2, fill: "#3b403c" }, svg); });
  }
  function needle(svg, len, width, color, tail) {
    const g = el("g", { class: "needle-g" }, svg);
    el("path", { d: `M${C - width} ${C + (tail || 14)} L${C - width * 0.55} ${C - len + 8} L${C} ${C - len} L${C + width * 0.55} ${C - len + 8} L${C + width} ${C + (tail || 14)} Z`, class: "needle", fill: color || "#f4f4ef" }, g);
    return g;
  }
  function hub(svg) { el("circle", { cx: C, cy: C, r: 7, class: "hub" }, svg); }
  const rot = (g, a) => g.setAttribute("transform", `rotate(${a} ${C} ${C})`);

  /* Generic round dial. */
  function dial(cfg) {
    const svg = el("svg", { viewBox: "0 0 200 200", "aria-hidden": "true" });
    base(svg);
    const { min, max, a0, a1 } = cfg;
    const ang = v => a0 + ((Math.min(max, Math.max(min, v)) - min) / (max - min)) * (a1 - a0);
    (cfg.arcs || []).forEach(arc => el("path", { d: arcPath(ang(arc.from), ang(arc.to), 80), stroke: arc.color, "stroke-width": 7, fill: "none" }, svg));
    for (let v = min; v <= max + 1e-6; v += cfg.minor) {
      const major = Math.abs(((v - min) / cfg.major) - Math.round((v - min) / cfg.major)) < 1e-6;
      const a = ang(v), [x0, y0] = pt(a, major ? 70 : 76), [x1, y1] = pt(a, 85);
      el("line", { x1: x0, y1: y0, x2: x1, y2: y1, class: "tick", "stroke-width": major ? 3 : 1.4 }, svg);
      if (major && cfg.labels !== false) {
        const [tx, ty] = pt(a, 56);
        const t = el("text", { x: tx, y: ty + 6, "text-anchor": "middle", "font-size": cfg.fontSize || 17 }, svg);
        t.textContent = cfg.fmt ? cfg.fmt(v) : v;
      }
    }
    const title = el("text", { x: C, y: C + 34, "text-anchor": "middle", "font-size": 12, opacity: 0.75 }, svg);
    title.textContent = cfg.title;
    if (cfg.unit) { const u = el("text", { x: C, y: C - 26, "text-anchor": "middle", "font-size": 11, opacity: 0.6 }, svg); u.textContent = cfg.unit; }
    const n = needle(svg, 80, 4.5);
    hub(svg);
    let shown = min;
    return { svg, set(v) { shown = v; rot(n, ang(v)); } };
  }

  function attitude() {
    const svg = el("svg", { viewBox: "0 0 200 200", "aria-hidden": "true" });
    el("circle", { cx: C, cy: C, r: 97, class: "bezel" }, svg);
    const clipId = "ai-clip-" + Math.random().toString(36).slice(2, 7);
    const defs = el("defs", {}, svg);
    const cp = el("clipPath", { id: clipId }, defs);
    el("circle", { cx: C, cy: C, r: 90 }, cp);
    const world = el("g", { "clip-path": `url(#${clipId})` }, svg);
    const ball = el("g", {}, world);
    el("rect", { x: -200, y: -400, width: 600, height: 500, fill: "#3f7fb8" }, ball);
    el("rect", { x: -200, y: 100, width: 600, height: 500, fill: "#6a4a2b" }, ball);
    el("line", { x1: -200, y1: 100, x2: 400, y2: 100, stroke: "#fff", "stroke-width": 2.5 }, ball);
    for (let p = -30; p <= 30; p += 10) {
      if (!p) continue;
      const y = 100 - p * 2.4, w = Math.abs(p) % 20 ? 18 : 30;
      el("line", { x1: C - w, y1: y, x2: C + w, y2: y, stroke: "#fff", "stroke-width": 1.6, opacity: 0.85 }, ball);
    }
    // Bank scale
    const bankScale = el("g", {}, svg);
    [-60, -30, -20, -10, 0, 10, 20, 30, 60].forEach(a => {
      const [x0, y0] = pt(a, 80), [x1, y1] = pt(a, a % 30 ? 86 : 89);
      el("line", { x1: x0, y1: y0, x2: x1, y2: y1, stroke: "#fff", "stroke-width": a % 30 ? 1.5 : 3 }, bankScale);
    });
    const pointer = el("path", { d: `M${C} 22 l-6 -10 h12 z`, fill: "#f2c230" }, svg);
    // Fixed miniature aircraft
    el("path", { d: `M${C - 46} ${C} h30 l8 8 l8 -8 h30`, fill: "none", stroke: "#f2c230", "stroke-width": 4.5, "stroke-linecap": "round", "stroke-linejoin": "round" }, svg);
    el("circle", { cx: C, cy: C, r: 3.5, fill: "#f2c230" }, svg);
    const lbl = el("text", { x: C, y: 180, "text-anchor": "middle", "font-size": 11, opacity: 0.8 }, svg);
    lbl.textContent = "GYRO HORIZON";
    return {
      svg,
      set(pitch, bank) {
        ball.setAttribute("transform", `rotate(${-bank} ${C} ${C}) translate(0 ${pitch * 2.4})`);
        rot(pointer, 0);
        bankScale.setAttribute("transform", `rotate(${-bank} ${C} ${C})`);
      }
    };
  }

  function altimeter() {
    const svg = el("svg", { viewBox: "0 0 200 200", "aria-hidden": "true" });
    base(svg);
    for (let i = 0; i < 50; i++) {
      const a = i * 7.2, major = i % 5 === 0, [x0, y0] = pt(a, major ? 72 : 78), [x1, y1] = pt(a, 86);
      el("line", { x1: x0, y1: y0, x2: x1, y2: y1, class: "tick", "stroke-width": major ? 3 : 1.3 }, svg);
      if (major) { const [tx, ty] = pt(a, 59); const t = el("text", { x: tx, y: ty + 7, "text-anchor": "middle", "font-size": 20 }, svg); t.textContent = i / 5; }
    }
    const t = el("text", { x: C, y: C + 36, "text-anchor": "middle", "font-size": 11, opacity: 0.7 }, svg); t.textContent = "ALT";
    const u = el("text", { x: C, y: C - 28, "text-anchor": "middle", "font-size": 10, opacity: 0.6 }, svg); u.textContent = "×100 FT";
    const tenK = needle(svg, 38, 2.5, "#f2c230", 8);
    const thou = needle(svg, 54, 5.5);
    const hund = needle(svg, 82, 3.2);
    hub(svg);
    return { svg, set(ft) { rot(hund, (ft % 1000) / 1000 * 360); rot(thou, (ft % 10000) / 10000 * 360); rot(tenK, (ft % 100000) / 100000 * 360); } };
  }

  function heading() {
    const svg = el("svg", { viewBox: "0 0 200 200", "aria-hidden": "true" });
    base(svg);
    const card = el("g", {}, svg);
    for (let h = 0; h < 360; h += 5) {
      const major = h % 30 === 0, [x0, y0] = pt(h, major ? 72 : h % 10 ? 80 : 76), [x1, y1] = pt(h, 86);
      el("line", { x1: x0, y1: y0, x2: x1, y2: y1, class: "tick", "stroke-width": major ? 2.6 : 1.2 }, card);
      if (major) {
        const [tx, ty] = pt(h, 58);
        const lab = { 0: "N", 90: "E", 180: "S", 270: "W" }[h] || String(h / 10);
        const tt = el("text", { x: tx, y: ty + 6, "text-anchor": "middle", "font-size": lab.length === 1 && isNaN(lab) ? 20 : 15, transform: `rotate(${h} ${tx} ${ty})` }, card);
        tt.textContent = lab;
        if (isNaN(lab)) tt.setAttribute("fill", "#f2c230");
      }
    }
    el("path", { d: `M${C} 10 l-7 12 h14 z`, fill: "#f2c230" }, svg);
    el("path", { d: `M${C - 22} ${C + 6} h44 M${C} ${C - 22} v40 M${C - 10} ${C + 18} h20`, stroke: "#f4f4ef", "stroke-width": 3.5, fill: "none", "stroke-linecap": "round" }, svg);
    return { svg, set(hdg) { card.setAttribute("transform", `rotate(${-hdg} ${C} ${C})`); } };
  }

  window.Gauges = { dial, attitude, altimeter, heading };
})();
