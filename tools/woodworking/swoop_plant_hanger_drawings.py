#!/usr/bin/env python3
"""SVG drawings for the Fixed Swoop Plant Hanger plan.

Usage: python3 tools/woodworking/swoop_plant_hanger_drawings.py
Writes static/static/woodworking/swoop-hanger-{side,templates}.svg and prints
the derived numbers the plan page quotes (curve ordinates, loads, grain check).
Geometry is in inches.

Side-view coordinates: x = out from the backplate's front face, y = up from the
top of the arm's root (where the arm meets the backplate). The arm is one
band-sawn swoop with its grain running horizontally, Domino'd to the face of a
vertical-grain backplate. This is the swing-arm hanger's arm with the pivot
(leg, knuckles, bolts) removed. fit_check() refuses geometry that thins the arm
or puts a Domino or the eye bolt where it doesn't fit, and grain_check() refuses
a curve whose grain runout would leave the arm weak. Edit the constants and
re-run. Reuses the Drawing helper from modern_craftsman_drawings.py.
"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from modern_craftsman_drawings import Drawing, frac as _frac


def frac(v):
    """frac() with a space between whole inches and a typed-out fraction (1 13/16″)."""
    s = _frac(abs(v))
    whole = round(abs(v) * 16) // 16
    if whole and '/' in s:
        s = f"{whole} {s[len(str(whole)):]}"
    return ('−' if v < 0 else '') + s


# ---- backplate (design) -----------------------------------------------------
BP_T, BP_W = 1.5, 3.5          # backplate thickness off the wall x width
BP_ABOVE = 2.5                 # backplate above the arm's top at the wall
BP_BELOW = 2.5                 # backplate below the arm root's bottom edge
SCREW_INSET = 1.25             # wall-screw centres from the backplate's ends

# ---- arm (design) -----------------------------------------------------------
ARM_T = 1.5                    # arm thickness (along the wall)
ARM_L = 14.0                   # arm tip, out from the backplate face
ROOT_D = 6.0                   # arm depth where it meets the backplate
ARM_D = 2.0                    # arm depth along the level tip
RISE = 2.25                    # top of the swoop rises this much above the root top
S_X0, S_X1 = 1.0, 10.0         # top S runs between these (level before and after)
EYE_X = 12.0                   # chain point, out from the backplate face (on the level tip)
UNDER_ANGLE = 60.0             # underside leaves the backplate at this angle from horizontal
K1, K2 = 3.0, 3.0              # underside Bezier handle lengths (shape of the swoop)
DOMINO_Y = (-1.75, -3.25, -4.75)   # 8x40 Dominos, arm root to backplate (y from root top)

# ---- load (design) ----------------------------------------------------------
DESIGN_LOAD = 30.0
CHAIN_SHOWN = 8.0
POT_SKETCH = (9.0, 6.5)

DOM_8 = (8 / 25.4, 22 / 25.4)

# ---- wood strength for the grain check (white oak, clear, est.) -------------
F_PAR = 15000.0                # bending / tension along the grain, psi (modulus of rupture)
F_PERP = 800.0                 # tension across the grain, psi
GRAIN_MARGIN_MIN = 10.0        # refuse any curve with less margin than this

EXTRA = """
<style>
  .wall{fill:url(#wallh);stroke:#555;stroke-width:1}
  .post{fill:#dcb988;stroke:#4a3320;stroke-width:1.3}
  .arm{fill:#ecd2ac;stroke:#4a3320;stroke-width:1.3;stroke-linejoin:round}
  .dom{fill:#f6e7a8;stroke:#8a6d1c;stroke-width:1;stroke-dasharray:3 2}
  .metal{fill:#9a9a9a;stroke:#444;stroke-width:1}
  .pot{fill:#eeeeea;stroke:#888;stroke-width:1;stroke-dasharray:4 3}
  .axis{stroke:#b0452b;stroke-width:1;stroke-dasharray:8 3 2 3;fill:none}
  .grain{stroke:#8a6a45;stroke-width:1;fill:none;opacity:.7}
  .grid{stroke:#c9d6e6;stroke-width:.7}
  .grid5{stroke:#9db3cf;stroke-width:1}
  .tmpl{fill:#f3dfbf;stroke:#2b1a0f;stroke-width:1.8}
</style>
<defs>
  <pattern id="wallh" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="6" stroke="#999" stroke-width="1"/>
  </pattern>
</defs>
"""

# ---------------------------------------------------------------------------
# geometry
# ---------------------------------------------------------------------------

BP_TOP = BP_ABOVE
BP_BOT = -ROOT_D - BP_BELOW
SCREW_Y = (BP_TOP - SCREW_INSET, BP_BOT + SCREW_INSET)


def top_y(x):
    """Top edge of the swoop: level, smoothstep S up RISE, level to the tip."""
    t = min(1.0, max(0.0, (x - S_X0) / (S_X1 - S_X0)))
    return RISE * (3 * t * t - 2 * t ** 3)


def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1])


def under_ctrl():
    a = math.radians(UNDER_ANGLE)
    p0 = (0.0, -ROOT_D)
    p1 = (p0[0] + K1 * math.cos(a), p0[1] + K1 * math.sin(a))
    p3 = (S_X1, RISE - ARM_D)
    p2 = (p3[0] - K2, p3[1])
    return p0, p1, p2, p3


def under_pts(n=60):
    c = under_ctrl()
    return [bezier(*c, i / n) for i in range(n + 1)]


def under_y(x):
    """Underside height at x (Bezier between the root and S_X1, level after)."""
    if x >= S_X1:
        return RISE - ARM_D
    pts = under_pts(400)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return -ROOT_D


def arm_outline(n=48):
    """Arm profile (x from the backplate face to the tip), y up."""
    xs = [0.0, S_X0] + [S_X0 + (S_X1 - S_X0) * i / n for i in range(1, n + 1)] + [ARM_L]
    top = [(x, top_y(x)) for x in xs]
    bottom = [(ARM_L, RISE - ARM_D), (S_X1, RISE - ARM_D)] + list(reversed(under_pts(n)))
    return top + bottom


def edge_angle_deg(f, x, h=0.02):
    """Angle (degrees from the grain) of the curve y = f(x) at x. The grain runs horizontal."""
    return abs(math.degrees(math.atan((f(x + h) - f(x - h)) / (2 * h))))


def grain_check():
    """Bending stress along the arm against the strength of the wood where the grain runs out.

    Wherever a cut edge crosses the grain at angle t, the fibres there are cut short and the
    wood is only as strong as Hankinson's formula allows: F = P*Q / (P sin^2 t + Q cos^2 t).
    Returns (min margin, x of the minimum, steepest edge angle, x of the steepest).
    """
    worst, worst_x = 1e9, 0.0
    steep, steep_x = 0.0, 0.0
    n = int(EYE_X * 20)
    for i in range(n + 1):
        x = EYE_X * i / n
        depth = top_y(x) - under_y(x)
        sigma = 6 * DESIGN_LOAD * (EYE_X - x) / (ARM_T * depth ** 2)
        t = math.radians(max(edge_angle_deg(top_y, x), edge_angle_deg(under_y, x)))
        f = F_PAR * F_PERP / (F_PAR * math.sin(t) ** 2 + F_PERP * math.cos(t) ** 2)
        if sigma > 0 and f / sigma < worst:
            worst, worst_x = f / sigma, x
        a = math.degrees(t)
        if a > steep:
            steep, steep_x = a, x
    return worst, worst_x, steep, steep_x


def loads():
    root_m = DESIGN_LOAD * EYE_X
    dom_lever = max(DOMINO_Y) + ROOT_D                       # top Domino above the root's bearing edge
    dom_t = root_m / dom_lever
    m_wall = DESIGN_LOAD * (EYE_X + BP_T)
    withdraw = m_wall / (SCREW_Y[0] - BP_BOT)
    return dict(root_m=root_m, dom_t=dom_t, dom_lever=dom_lever, m_wall=m_wall, withdraw=withdraw)


def fit_check():
    probs = []
    if EYE_X - 0.5 < S_X1 or EYE_X + 0.75 > ARM_L:
        probs.append("eye bolt must sit on the level tip")
    depths = [top_y(x) - under_y(x) for x in [0.1 * i for i in range(int(ARM_L * 10))]]
    if min(depths) < ARM_D - 0.02:
        probs.append(f"arm thins to {min(depths):.2f} somewhere (want >= {ARM_D})")
    if min(DOMINO_Y) - DOM_8[1] / 2 < -ROOT_D + 0.5:
        probs.append("lowest Domino too close to the root's bottom edge")
    if max(DOMINO_Y) + DOM_8[1] / 2 > -0.5:
        probs.append("top Domino too close to the arm's top edge")
    for sy in SCREW_Y:
        for yc in DOMINO_Y:
            if abs(sy - yc) < DOM_8[1] / 2 + 0.5:
                probs.append(f"wall screw at {sy:.2f} is too near the Domino at {yc:.2f}")
    margin, mx, _, _ = grain_check()
    if margin < GRAIN_MARGIN_MIN:
        probs.append(f"grain runout leaves only {margin:.1f}x margin at {mx:.1f} in (want >= {GRAIN_MARGIN_MIN:g}x)")
    return probs


# ---------------------------------------------------------------------------
# drawings
# ---------------------------------------------------------------------------

def P(pts):
    return [(x, -y) for x, y in pts]


def side(path):
    s = 18
    pot_top = -(RISE - ARM_D) + 1.25 + CHAIN_SHOWN       # drawing y (down)
    bot = max(-BP_BOT, pot_top + POT_SKETCH[1]) + 1
    d = Drawing(1120, int((BP_TOP + bot) * s) + 200, 420, 100 + BP_TOP * s, s=s)
    d.text(20, 26, f"Side elevation, fixed swoop plant hanger — 1 in = {s} px", "h", "start")
    d.rect(-BP_T - 0.9, -BP_TOP - 1, -BP_T, bot, "wall")
    d.rect(-BP_T, -BP_TOP, 0, -BP_BOT, "post")
    for sy in SCREW_Y:
        d.add(f'<circle class="metal" cx="{d.x(-BP_T / 2):.1f}" cy="{d.y(-sy):.1f}" r="4.5"/>')
    d.poly(P(arm_outline()), "arm")
    for yc in DOMINO_Y:
        d.rect(-0.79, -yc - DOM_8[1] / 2, 0.79, -yc + DOM_8[1] / 2, "dom")
    # eye bolt, chain, planter
    ty = -RISE
    d.rect(EYE_X - 0.125, ty - 0.2, EYE_X + 0.125, ty + ARM_D + 0.35, "metal")
    d.rect(EYE_X - 0.5, ty - 0.2, EYE_X + 0.5, ty, "metal")
    ey = ty + ARM_D + 0.7
    d.add(f'<circle cx="{d.x(EYE_X):.1f}" cy="{d.y(ey):.1f}" r="{0.45*s:.1f}" fill="none" stroke="#444" stroke-width="2.5"/>')
    yy, i = ty + ARM_D + 1.25, 0
    while yy < pot_top - 0.1:
        w = 0.32 if i % 2 == 0 else 0.12
        d.add(f'<ellipse cx="{d.x(EYE_X):.1f}" cy="{d.y(yy + 0.35):.1f}" rx="{w*s:.1f}" ry="{0.4*s:.1f}" fill="none" stroke="#444" stroke-width="1.8"/>')
        yy += 0.6
        i += 1
    pd, ph = POT_SKETCH
    for dx in (-pd / 2 + 0.5, pd / 2 - 0.5):
        d.line(EYE_X, pot_top, EYE_X + dx, pot_top + 1.8, "pot")
    d.poly([(EYE_X - pd / 2, pot_top + 1.8), (EYE_X + pd / 2, pot_top + 1.8),
            (EYE_X + pd / 2 - 1, pot_top + ph), (EYE_X - pd / 2 + 1, pot_top + ph)], "pot")
    # dims
    d.dim_h(-BP_T, ARM_L, 52, f"{frac(ARM_L + BP_T)} off the wall", pyo=d.y(-BP_TOP))
    d.dim_h(0, EYE_X, 76, f"{frac(EYE_X)} from the backplate to the chain", pyo=d.y(-RISE))
    d.dim_v(-BP_TOP, -BP_BOT, d.x(-BP_T) - 44, f"backplate {frac(BP_TOP - BP_BOT)}", pxo=d.x(-BP_T))
    d.dim_v_text(-RISE, -RISE + ARM_D, d.x(ARM_L) + 14, f"{frac(ARM_D)} deep at the tip", pxo=d.x(ARM_L))
    d.dim_v_text(0, ROOT_D, d.x(0) + 3.2 * s, f"root {frac(ROOT_D)}", pxo=d.x(0) + 1.0 * s, side="right")
    # callouts
    lx = d.x(max(ARM_L, EYE_X + POT_SKETCH[0] / 2)) + 22
    L = lambda fx, fy, ly, txt: d.leader(d.x(fx), d.y(fy), lx, ly, txt)
    L(EYE_X, ty + 0.4, d.y(ty) + 44, "¼-20 forged eye bolt")
    L(EYE_X + 0.3, ty + ARM_D + 4, d.y(ty) + 74, "rated chain + quick link, WLL ≥ 60 lb")
    L(EYE_X + pd / 2 - 0.6, pot_top + ph / 2, d.y(pot_top + ph / 2), f"planter, for scale (≤ {DESIGN_LOAD:.0f} lb wet)")
    L(0.5, -DOMINO_Y[1], d.y(ty) + 104, "3 × 8×40 Domino, arm → backplate")
    L(4.5, -top_y(4.5) + 0.4, d.y(ty) + 134, "arm: grain horizontal")
    lxl = d.x(-BP_T) - 70
    LL = lambda fx, fy, ly, txt: d.leader(d.x(fx), d.y(fy), lxl, ly, txt, "end")
    LL(-BP_T / 2, -BP_TOP + 0.6, d.y(-BP_TOP) + 14, "backplate: grain vertical")
    LL(-BP_T / 2, -SCREW_Y[0], d.y(-SCREW_Y[0]) - 30, "wall screw into a stud (2)")
    LL(-BP_T / 2, -SCREW_Y[1], d.y(-SCREW_Y[1]) + 22, "second screw, same stud")
    yb = d.y(bot) + 28
    d.text(20, yb, "Yellow dashed = Dominos. Thin brown lines = grain direction. Planter shown for scale.", "n", "start")
    d.text(20, yb + 16, f"Backplate {frac(BP_T)} × {frac(BP_W)} × {frac(BP_TOP - BP_BOT)}; wall screws {frac(SCREW_INSET)} from each end, "
           f"clear of the Dominos.", "n", "start")
    d.save(path, "Fixed swoop plant hanger, side elevation", EXTRA)


def templates(path):
    s = 34
    yoff = RISE
    d = Drawing(1080, 700, 60, 90 + yoff * s, s=s)
    d.text(20, 26, f"Band-saw template — arm, 1 in = {s} px; grid = 1″ (print, then check one grid square)", "h", "start")
    rel = [(x, -y) for x, y in arm_outline(60)]
    d.poly(rel, "tmpl")
    for i in range(0, math.ceil(ARM_L) + 1):
        d.line(i, -math.ceil(RISE), i, ROOT_D, "grid5" if i % 5 == 0 else "grid")
    for j in range(-math.ceil(RISE), int(ROOT_D) + 1):
        d.line(0, j, ARM_L, j, "grid5" if j % 5 == 0 else "grid")
    d.add('<polygon fill="none" stroke="#2b1a0f" stroke-width="1.8" points="' +
          ' '.join(f'{d.x(a):.1f},{d.y(b):.1f}' for a, b in rel) + '"/>')
    for yc in DOMINO_Y:
        d.rect(0, -yc - DOM_8[1] / 2, 0.79, -yc + DOM_8[1] / 2, "dom")
    d.line(EYE_X, -RISE - 0.2, EYE_X, -RISE + ARM_D + 0.2, "axis")
    d.text(d.x(EYE_X), d.y(-RISE + ARM_D) + 16, "eye", "n")
    for xk in (S_X0, S_X1):
        d.line(xk, -top_y(xk) - 0.35, xk, -top_y(xk) + 0.35, "axis")
    for gy in (-1.0, 1.5, 3.0, 4.5):
        d.line(0.3, gy, ARM_L - 0.3, gy, "grain")
    d.text(d.x(0) + 6, d.y(ROOT_D) + 14, "root end (glues to the backplate)", "n", "start")
    d.text(d.x(ARM_L) - 4, d.y(3.0) - 6, "grain →", "n", "end")
    d.dim_v(0, ROOT_D, d.x(0) - 14, frac(ROOT_D), pxo=d.x(0))
    d.dim_v_text(-RISE, -RISE + ARM_D, d.x(ARM_L) + 12, frac(ARM_D), pxo=d.x(ARM_L))
    d.dim_h(0, ARM_L, d.y(ROOT_D) + 26, f"{frac(ARM_L)}", pyo=d.y(ROOT_D), below=True)
    d.text(d.x(0), d.y(ROOT_D) + 64,
           f"ARM (cut 1) — blank {frac(ARM_T)} × {frac(ROOT_D + RISE)} × {frac(ARM_L + 0.5)}, grain along the length "
           f"(parallel to the blank's long edges). Top: level for {frac(S_X0)}, then an S rising {frac(RISE)} to {frac(S_X1)}, level to the tip.",
           "n", "start")
    d.text(d.x(0), d.y(ROOT_D) + 80,
           f"Underside: leaves the root's bottom corner at {UNDER_ANGLE:.0f}° and sweeps into the level tip at {frac(S_X1)}.",
           "n", "start")
    d.text(d.x(0), d.y(ROOT_D) + 96, "Plot both edges from the ordinate tables on the plan page and bend a thin batten through the points.", "n", "start")
    d.save(path, "Fixed swoop plant hanger, band-saw template for the arm", EXTRA)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "..", "static", "static", "woodworking")
    os.makedirs(out, exist_ok=True)
    probs = fit_check()
    for p in probs:
        print("FIT:", p)
    if probs:
        raise SystemExit(1)
    side(os.path.join(out, "swoop-hanger-side.svg"))
    templates(os.path.join(out, "swoop-hanger-templates.svg"))
    L = loads()
    gm, gx, steep, steep_x = grain_check()
    print(f"backplate {BP_TOP - BP_BOT:.3f} tall; screws at y {SCREW_Y} (arm top at the wall = 0)")
    print(f"off the wall {ARM_L + BP_T:.2f}; backplate face to chain {EYE_X:.2f}")
    print("top ordinates (from root):", ", ".join(f"{x:g}:{top_y(x):.3f}" for x in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
    print("underside ordinates (from root):", ", ".join(f"{x:g}:{under_y(x):.3f}" for x in [0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 9]))
    print("depth min:", f"{min(top_y(x) - under_y(x) for x in [0.1 * i for i in range(int(ARM_L * 10))]):.2f}")
    print(f"steepest cut edge {steep:.0f}° to the grain at {steep_x:.1f} in; "
          f"worst grain margin {gm:.0f}x at {gx:.1f} in; top edge max {max(edge_angle_deg(top_y, 0.1 * i) for i in range(1, 140)):.0f}°")
    print(f"root moment {L['root_m']:.0f} in-lb, top Domino lever {L['dom_lever']:.2f}, tension ≈ {L['dom_t']:.0f} lb, "
          f"wall moment {L['m_wall']:.0f} in-lb, top screw ≈ {L['withdraw']:.0f} lb")
    print("wrote 2 SVGs to", os.path.normpath(out))
