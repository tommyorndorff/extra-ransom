#!/usr/bin/env python3
"""SVG drawings for the Plant-Hanger Wall Bracket plan.

Usage: python3 tools/woodworking/plant_hanger_bracket_drawings.py
Writes public/static/woodworking/plant-hanger-bracket-{side,templates}.svg
and prints the derived numbers the plan page quotes (arc radii, template
ordinates, loads). Geometry is in inches. Side-view coordinates:
x = out from the backplate's front face, y = up from the arm's top face
(so most of the build is at negative y). Edit the constants and re-run.
Reuses the Drawing helper from modern_craftsman_drawings.py.
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

# ---- bracket (design) -------------------------------------------------------
BP_T, BP_W = 1.5, 3.5          # backplate thickness (off the wall) x width
BP_ABOVE = 2.5                 # backplate top above the arm's top face
BP_BELOW = 16.5                # backplate bottom below the arm's top face
ARM_T, ARM_L = 1.5, 17.0       # arm: two 3/4 laminations; length out from the backplate
ARM_D = 2.25                   # arm depth along its straight run
ARM_D_WALL = 5.0               # arm depth where it meets the backplate
CURVE_X = 4.0                  # underside curve is tangent to the straight run here
EYE_X = 13.0                   # chain point, out from the backplate face (on the flat tip)
TOP_RISE = 1.25                # the arm's top rises this much in a gentle S toward the tip
S_X0, S_X1 = 7.0, 12.0         # S runs between these: flat before (brace Domino landing), flat after (eye bolt)
BR_T, BR_W = 1.0, 1.75         # brace thickness x band width (square to the curve)
BR_FOOT_Y = -10.0              # brace foot centre on the backplate
BR_TOP_X = 5.5                 # brace top centre on the arm underside
BR_SAG = 0.9                   # how far the brace bows outward (down-right) from its chord
SCREW_Y = (BP_ABOVE - 1.25, -BP_BELOW + 1.5)   # wall screws, on the backplate centreline

# ---- hanging load (design) ----------------------------------------------------
EYE_DROP = 1.25                # eye bolt's eye below the arm underside
CHAIN_SHOWN = 8.0              # chain drawn in the side view (yours can be any length)
POT_SKETCH = (8.0, 6.0)        # a hanging planter, for scale only (dia x height)
DESIGN_LOAD = 30.0             # lb the bracket and hardware are sized for

DOM_6 = (6 / 25.4, 20 / 25.4)
DOM_8 = (8 / 25.4, 22 / 25.4)

EXTRA = """
<style>
  .wall{fill:url(#wallh);stroke:#555;stroke-width:1}
  .post{fill:#dcb988;stroke:#4a3320;stroke-width:1.3}
  .dom{fill:#f6e7a8;stroke:#8a6d1c;stroke-width:1;stroke-dasharray:3 2}
  .metal{fill:#b9a26a;stroke:#5c4a1e;stroke-width:1.1}
  .pot{fill:#eeeeea;stroke:#888;stroke-width:1;stroke-dasharray:4 3}
  .grid{stroke:#c9d6e6;stroke-width:.7}
  .grid5{stroke:#9db3cf;stroke-width:1}
  .tmpl{fill:#f3dfbf;stroke:#2b1a0f;stroke-width:1.8}
  .ctr{stroke:#b0452b;stroke-width:1;stroke-dasharray:6 3;fill:none}
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

def arm_curve():
    """Underside fillet: circle tangent to the straight underside at CURVE_X,
    through (0, -ARM_D_WALL). Returns (radius, centre)."""
    a, b = CURVE_X, ARM_D_WALL - ARM_D
    r = (a * a + b * b) / (2 * b)
    return r, (CURVE_X, -ARM_D - r)


def arm_top(x):
    """Height of the arm's top face above its height at the wall: a smoothstep S
    (zero slope at both ends, so the landing and the tip stay flat)."""
    t = min(1.0, max(0.0, (x - S_X0) / (S_X1 - S_X0)))
    return TOP_RISE * (3 * t * t - 2 * t ** 3)


def arm_outline(n=24):
    r, (cx, cy) = arm_curve()
    xs = [0.0] + [S_X0 + (S_X1 - S_X0) * i / n for i in range(n + 1)] + [ARM_L]
    pts = [(x, arm_top(x)) for x in xs]
    pts += [(x, arm_top(x) - ARM_D) for x in reversed(xs) if x >= CURVE_X]
    pts.append((CURVE_X, -ARM_D))
    a0 = math.atan2(-ARM_D - cy, CURVE_X - cx)              # straight up (pi/2)
    a1 = math.atan2(-ARM_D_WALL - cy, 0 - cx)
    for i in range(1, n + 1):
        a = a0 + (a1 - a0) * i / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def arm_depth_at(x):
    """Depth of the arm below its top face at x."""
    if x >= CURVE_X:
        return ARM_D
    r, (cx, cy) = arm_curve()
    return -(cy + math.sqrt(r * r - (x - cx) ** 2))


def brace_arc():
    """Brace centreline: circular arc foot -> top, bowed outward by BR_SAG."""
    fx, fy = 0.0, BR_FOOT_Y
    tx, ty = BR_TOP_X, -ARM_D
    c = math.hypot(tx - fx, ty - fy)
    ux, uy = (tx - fx) / c, (ty - fy) / c
    nx, ny = uy, -ux                                   # normal toward down-right (outward)
    r = (c * c / 4 + BR_SAG ** 2) / (2 * BR_SAG)
    mx, my = (fx + tx) / 2, (fy + ty) / 2
    cx, cy = mx - (r - BR_SAG) * nx, my - (r - BR_SAG) * ny
    return r, (cx, cy), (fx, fy), (tx, ty), c


def clip(poly, inside, intersect):
    out = []
    for i in range(len(poly)):
        p, q = poly[i - 1], poly[i]
        if inside(q):
            if not inside(p):
                out.append(intersect(p, q))
            out.append(q)
        elif inside(p):
            out.append(intersect(p, q))
    return out


def brace_outline(n=40, extend=0.35):
    """Band of width BR_W around the arc, trimmed to the wall (x >= 0) and the
    arm underside (y <= -ARM_D)."""
    r, (cx, cy), F, T, _ = brace_arc()
    a_f = math.atan2(F[1] - cy, F[0] - cx)
    a_t = math.atan2(T[1] - cy, T[0] - cx)
    a0, a1 = a_f + extend * (a_f - a_t), a_t + extend * (a_t - a_f)
    outer = [(cx + (r + BR_W / 2) * math.cos(a0 + (a1 - a0) * i / n),
              cy + (r + BR_W / 2) * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    inner = [(cx + (r - BR_W / 2) * math.cos(a0 + (a1 - a0) * i / n),
              cy + (r - BR_W / 2) * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    poly = outer + inner[::-1]
    poly = clip(poly, lambda p: p[0] >= 0,
                lambda p, q: (0.0, p[1] + (q[1] - p[1]) * (0 - p[0]) / (q[0] - p[0])))
    poly = clip(poly, lambda p: p[1] <= -ARM_D,
                lambda p, q: (p[0] + (q[0] - p[0]) * (-ARM_D - p[1]) / (q[1] - p[1]), -ARM_D))
    return poly


def tangent_angles():
    """Brace tangent at foot and top, degrees from horizontal."""
    r, (cx, cy), F, T, _ = brace_arc()
    def tang(p):
        rx, ry = p[0] - cx, p[1] - cy
        tx, ty = -ry, rx                     # perpendicular to the radius
        if tx < 0:
            tx, ty = -tx, -ty
        return math.degrees(math.atan2(ty, tx))
    return tang(F), tang(T)


def end_lengths():
    af, at = tangent_angles()
    foot = BR_W / math.cos(math.radians(af))      # vertical cut against the backplate
    top = BR_W / math.sin(math.radians(at))       # horizontal cut against the arm
    return foot, top


def check_geometry():
    """The S must leave flat surfaces where the Domino and the eye bolt go."""
    assert S_X0 >= CURVE_X, "S-curve must start after the underside haunch"
    bt = [p[0] for p in brace_outline() if abs(p[1] + ARM_D) < 1e-6]
    assert bt and max(bt) + 0.5 <= S_X0, f"brace top ({max(bt):.2f}) needs 1/2 in of flat before the S at {S_X0}"
    assert EYE_X - 0.5 >= S_X1, "eye bolt must sit on the flat tip, past the S"


def loads():
    r_bp = EYE_X + BP_T                          # lever arm to the wall
    m_wall = DESIGN_LOAD * r_bp
    pivot_to_top = BP_ABOVE + BP_BELOW - (BP_ABOVE - SCREW_Y[0])
    withdraw = m_wall / pivot_to_top
    arm_dom_y = (-1.875 - 3.625) / 2
    h = arm_dom_y - BR_FOOT_Y
    tension = DESIGN_LOAD * EYE_X / h
    return dict(m_wall=m_wall, withdraw=withdraw, tension=tension, h=h)


# ---------------------------------------------------------------------------
# drawings
# ---------------------------------------------------------------------------

def P(d, pts):
    """Side-view points (y up) to a Drawing with y down."""
    return [(x, -y) for x, y in pts]


def side(path):
    s = 15
    top = BP_ABOVE
    te = arm_top(EYE_X)                      # arm top at the eye, above the wall-end top
    pot_top = ARM_D + EYE_DROP + CHAIN_SHOWN - te
    bot = max(BP_BELOW, pot_top + POT_SKETCH[1]) + 1
    d = Drawing(1000, int((top + bot) * s) + 170, 300, 90 + top * s, s=s)
    d.text(20, 26, f"Side elevation, plant-hanger bracket — 1 in = {s} px", "h", "start")
    # wall + backplate
    d.rect(-BP_T - 0.9, -BP_ABOVE - 1.5, -BP_T, bot, "wall")
    d.rect(-BP_T, -BP_ABOVE, 0, BP_BELOW, "post")
    for sy in SCREW_Y:
        d.add(f'<circle class="metal" cx="{d.x(-BP_T / 2):.1f}" cy="{d.y(-sy):.1f}" r="4"/>')
    # brace behind the arm
    d.poly(P(d, brace_outline()), "wood")
    d.poly(P(d, arm_outline()), "wood")
    # dominos
    for yc in (-1.875, -3.625):
        d.rect(-0.79, -yc - DOM_8[1] / 2, 0.79, -yc + DOM_8[1] / 2, "dom")
    r, (cx, cy), F, T, _ = brace_arc()
    d.rect(-0.79, -F[1] - DOM_6[1] / 2, 0.79, -F[1] + DOM_6[1] / 2, "dom")
    d.rect(T[0] - DOM_6[1] / 2, ARM_D - 0.79, T[0] + DOM_6[1] / 2, ARM_D + 0.79, "dom")
    # eye bolt and chain
    d.rect(EYE_X - 0.125, -0.2 - te, EYE_X + 0.125, ARM_D + 0.35 - te, "metal")
    d.rect(EYE_X - 0.5, -0.2 - te, EYE_X + 0.5, -te, "metal")
    ey = ARM_D + EYE_DROP / 2 + 0.1 - te
    d.add(f'<circle cx="{d.x(EYE_X):.1f}" cy="{d.y(ey):.1f}" r="{0.45*s:.1f}" fill="none" stroke="#5c4a1e" stroke-width="2.5"/>')
    yy = ARM_D + EYE_DROP - te
    i = 0
    while yy < pot_top - 0.1:
        w = 0.32 if i % 2 == 0 else 0.12
        d.add(f'<ellipse cx="{d.x(EYE_X):.1f}" cy="{d.y(yy + 0.35):.1f}" rx="{w*s:.1f}" ry="{0.4*s:.1f}" '
              f'fill="none" stroke="#5c4a1e" stroke-width="1.8"/>')
        yy += 0.6
        i += 1
    # a hanging planter, for scale (not part of the build)
    pd, ph = POT_SKETCH
    for dx in (-pd / 2 + 0.4, pd / 2 - 0.4):
        d.line(EYE_X, pot_top, EYE_X + dx, pot_top + 1.6, "pot")
    d.poly([(EYE_X - pd / 2, pot_top + 1.6), (EYE_X + pd / 2, pot_top + 1.6),
            (EYE_X + pd / 2 - 0.9, pot_top + ph), (EYE_X - pd / 2 + 0.9, pot_top + ph)], "pot")
    # dims
    d.dim_h(-BP_T, ARM_L, 52, f"{frac(ARM_L + BP_T)} off the wall", pyo=d.y(-BP_ABOVE))
    d.dim_h(0, EYE_X, 76, f"{frac(EYE_X)} to the chain", pyo=d.y(0))
    d.dim_v(-BP_ABOVE, BP_BELOW, d.x(-BP_T) - 40, f"backplate {frac(BP_ABOVE + BP_BELOW)}", pxo=d.x(-BP_T))
    tt = arm_top(ARM_L)
    d.dim_v_text(-tt, ARM_D - tt, d.x(ARM_L) + 14, f"arm {frac(ARM_D)} deep, {frac(ARM_T)} thick", pxo=d.x(ARM_L))
    # callouts
    lx = d.x(ARM_L) + 20
    sm = (S_X0 + S_X1) / 2
    d.leader(d.x(sm), d.y(-arm_top(sm)), lx, d.y(ARM_D) + 24,
             f"S-curve top, rises {frac(TOP_RISE)}")
    d.leader(d.x(EYE_X), d.y(ARM_D + 0.3 - te), lx, d.y(ARM_D) + 52, "¼-20 forged eye bolt, through")
    d.leader(d.x(EYE_X + 0.4), d.y(ARM_D + 4 - te), lx, d.y(ARM_D) + 82, "welded chain + quick link, WLL ≥ 60 lb")
    d.leader(d.x(EYE_X + pd / 2 - 0.5), d.y(pot_top + ph / 2), lx, d.y(pot_top + ph / 2),
             f"planter, for scale (≤ {DESIGN_LOAD:.0f} lb wet)")
    d.leader(d.x(-0.4), d.y(-F[1]), d.x(-BP_T) - 62, d.y(-F[1]) + 30, "6×40 Domino (brace foot)", "end")
    d.leader(d.x(-0.4), d.y(2.75), d.x(-BP_T) - 62, d.y(2.75) - 10, "2 × 8×40 Domino (arm)", "end")
    d.leader(d.x(-BP_T / 2), d.y(-SCREW_Y[0]), d.x(-BP_T) - 62, d.y(-SCREW_Y[0]) - 20, "wall screw into a stud (2)", "end")
    d.leader(d.x(BR_TOP_X + 0.4), d.y(ARM_D + 0.5), lx, d.y(ARM_D) + 112, "6×40 Domino (brace top)")
    d.leader(d.x(2.6), d.y(-(BR_FOOT_Y + 2.6)), d.x(-BP_T) - 62, d.y(-(BR_FOOT_Y + 2.6)) - 30,
             f"brace {frac(BR_T)} thick, {frac(BR_W)} band", "end")
    yb = d.y(bot) + 30
    d.text(20, yb, "Yellow dashed = Dominos. Grey dashed = a hanging planter, for scale.", "n", "start")
    d.text(20, yb + 16, f"Brace foot {frac(-BR_FOOT_Y)} below the arm top; brace top {frac(BR_TOP_X)} out on the arm underside. "
           f"Wall screws {frac(BP_ABOVE - SCREW_Y[0])} from the top and {frac(SCREW_Y[1] + BP_BELOW)} from the bottom.", "n", "start")
    d.save(path, "Plant-hanger bracket, side elevation", EXTRA)


def templates(path):
    s = 34
    r_arm, (acx, acy) = arm_curve()
    # arm template
    d = Drawing(1000, 900 + int(TOP_RISE * s), 50, 90 + TOP_RISE * s, s=s)
    d.text(20, 26, f"Band-saw templates — 1 in = {s} px; grid = 1″ (print, then check one grid square)", "h", "start")
    d.poly(P(d, arm_outline(48)), "tmpl")
    jt = -math.ceil(TOP_RISE)
    for i in range(0, int(ARM_L) + 1):
        d.line(i, jt, i, ARM_D_WALL, "grid5" if i % 5 == 0 else "grid")
    for j in range(jt, int(ARM_D_WALL) + 1):
        d.line(0, j, ARM_L, j, "grid5" if j % 5 == 0 else "grid")
    d.add(f'<polygon fill="none" stroke="#2b1a0f" stroke-width="1.8" points="' +
          ' '.join(f'{d.x(a):.1f},{d.y(-b):.1f}' for a, b in arm_outline(48)) + '"/>')
    d.text(d.x(ARM_L / 2 + 3), d.y(ARM_D_WALL) + 36, f"ARM (cut 1 after laminating) — {frac(ARM_T)} × {frac(ARM_D_WALL + TOP_RISE)} × {frac(ARM_L)} blank", "t")
    d.text(d.x(0.2), d.y(-0.25), "wall end (end grain to backplate)", "n", "start")
    d.add(f'<circle class="ctr" cx="{d.x(acx):.1f}" cy="{d.y(-acy):.1f}" r="3"/>')
    d.dim_h(0, CURVE_X, d.y(ARM_D_WALL) + 22, f"curve {frac(CURVE_X)}", pyo=d.y(ARM_D_WALL), below=True)
    d.dim_v_text(-TOP_RISE, ARM_D - TOP_RISE, d.x(ARM_L) + 12, frac(ARM_D), pxo=d.x(ARM_L))
    d.dim_v(0, ARM_D_WALL, d.x(0) - 14, frac(ARM_D_WALL), pxo=d.x(0))
    d.text(d.x(5), d.y(ARM_D_WALL) + 58, f"Underside curve: radius {frac(r_arm)}, centre {frac(acx)} out and "
           f"{frac(-acy)} below the top; tangent to the straight underside at {frac(CURVE_X)}.", "n", "start")
    d.text(d.x(5), d.y(ARM_D_WALL) + 76, f"Top and underside S: flat to {frac(S_X0)}, rising {frac(TOP_RISE)} by {frac(S_X1)} "
           f"(ordinates in the plan); the underside follows {frac(ARM_D)} below the top.", "n", "start")
    for xk in (S_X0, S_X1):
        d.line(xk, -arm_top(xk) - 0.35, xk, -arm_top(xk) + 0.35, "ctr")
    te = arm_top(EYE_X)
    d.line(EYE_X, -0.2 - te, EYE_X, ARM_D + 0.2 - te, "ctr")
    d.text(d.x(EYE_X), d.y(ARM_D - te) + 16, "eye", "n")
    # brace template
    poly = brace_outline(60)
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    bx0, by1 = min(xs), max(ys)
    bw, bh = max(xs) - bx0, max(ys) - min(ys)
    b = Drawing(1000, 900, 50, 390 + TOP_RISE * s, s=s)
    rel = [(x - bx0, by1 - y) for x, y in poly]
    b.poly(rel, "tmpl")
    for i in range(0, math.ceil(bw) + 1):
        b.line(i, 0, i, math.ceil(bh), "grid5" if i % 5 == 0 else "grid")
    for j in range(0, math.ceil(bh) + 1):
        b.line(0, j, math.ceil(bw), j, "grid5" if j % 5 == 0 else "grid")
    b.add(f'<polygon fill="none" stroke="#2b1a0f" stroke-width="1.8" points="' +
          ' '.join(f'{b.x(a):.1f},{b.y(c):.1f}' for a, c in rel) + '"/>')
    r, (cx, cy), F, T, chord = brace_arc()
    a_f, a_t = math.atan2(F[1] - cy, F[0] - cx), math.atan2(T[1] - cy, T[0] - cx)
    arc = [(cx + r * math.cos(a_f + (a_t - a_f) * k / 30) - bx0, by1 - (cy + r * math.sin(a_f + (a_t - a_f) * k / 30)))
           for k in range(31)]
    b.add('<polyline class="ctr" points="' + ' '.join(f'{b.x(a):.1f},{b.y(c):.1f}' for a, c in arc) + '"/>')
    b.rect(T[0] - bx0 - DOM_6[1] / 2, 0, T[0] - bx0 + DOM_6[1] / 2, 0.79, "dom")
    b.rect(0, by1 - F[1] - DOM_6[1] / 2, 0.79, by1 - F[1] + DOM_6[1] / 2, "dom")
    af, at = tangent_angles()
    fl, tl = end_lengths()
    b.text(b.x(bw) + 30, b.y(0.4), f"BRACE (cut 1) — {frac(BR_T)} thick", "t", "start")
    b.text(b.x(bw) + 30, b.y(0.4) + 20, f"blank {frac(bw + 0.5)} × {frac(bh + 0.5)}", "n", "start")
    notes = [
        f"Centreline radius {frac(r)} (inner edge {frac(r - BR_W / 2)}, outer {frac(r + BR_W / 2)}).",
        f"Centre point: {frac(bx0 - cx)} left of and {frac(cy - by1)} above the grid's top-left corner,",
        "i.e. off the blank: swing both edges with a trammel from a scrap board.",
        f"Top end: cut level (sits on the arm underside), {frac(tl)} long, {at:.0f}° to the arm.",
        f"Foot end: cut plumb (against the backplate), {frac(fl)} long, {90 - af:.0f}° to the wall.",
        f"Chord foot → top {frac(chord)}; bow {frac(BR_SAG)}.",
    ]
    for k, t in enumerate(notes):
        b.text(b.x(bw) + 30, b.y(0.4) + 44 + 17 * k, t, "n", "start")
    b.text(b.x(0.1), b.y(-0.3), "top end (to the arm)", "n", "start")
    b.text(b.x(0.1), b.y(bh) + 18, "foot end (to the backplate) is the left edge", "n", "start")
    d.p.extend(b.p)
    d.save(path, "Plant-hanger bracket, band-saw templates for arm and brace", EXTRA)
    return (bw, bh), poly, bx0, by1


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "..", "public", "static", "woodworking")
    os.makedirs(out, exist_ok=True)
    side(os.path.join(out, "plant-hanger-bracket-side.svg"))
    (bw, bh), poly, bx0, by1 = templates(os.path.join(out, "plant-hanger-bracket-templates.svg"))
    r_arm, ac = arm_curve()
    r, c, F, T, chord = brace_arc()
    af, at = tangent_angles()
    fl, tl = end_lengths()
    L = loads()
    print(f"arm curve R={r_arm:.3f} centre=({ac[0]:.2f},{ac[1]:.2f})")
    check_geometry()
    print("arm top S ordinates:", ", ".join(f"{x:g}:{arm_top(x):.2f}" for x in [7, 8, 9, 9.5, 10, 11, 12]))
    print("arm depth ordinates:", ", ".join(f"{x:g}:{arm_depth_at(x):.2f}" for x in [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]))
    print(f"brace R={r:.3f} centre=({c[0]:.2f},{c[1]:.2f}) chord={chord:.2f} foot tangent {af:.1f}° top tangent {at:.1f}°")
    print(f"brace end cuts: foot {fl:.2f} top {tl:.2f}; blank {bw:.2f} x {bh:.2f}")
    print(f"design load {DESIGN_LOAD} lb at {EYE_X} in out")
    print(f"moment at wall {L['m_wall']:.0f} in-lb; top screw withdrawal ≈ {L['withdraw']:.0f} lb; "
          f"arm joint tension ≈ {L['tension']:.0f} lb (lever {L['h']:.2f})")
    print("wrote 2 SVGs to", os.path.normpath(out))
