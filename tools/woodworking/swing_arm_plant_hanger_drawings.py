#!/usr/bin/env python3
"""SVG drawings for the Swing-Arm Plant Hanger plan.

Usage: python3 tools/woodworking/swing_arm_plant_hanger_drawings.py
Writes static/static/woodworking/swing-arm-hanger-{side,plan,templates}.svg and
prints the derived numbers the plan page quotes (curve ordinates, swing limit,
clearances, loads). Geometry is in inches.

Side-view coordinates: x = out from the pivot axis, y = up from the top of the
leg. The swinging part is one swoop made of two pieces: a straight vertical
LEG (grain vertical) that carries both pivot bolts in its ends, and an ARM
(grain horizontal) whose deep root is Domino'd to the leg's outer face. The
swoop is band-sawn across the arm so the leg flows into the arm in one curve.
fit_check() refuses geometry that would bind or collide. Edit the constants
and re-run. Reuses the Drawing helper from modern_craftsman_drawings.py.
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


# ---- backplate and knuckles (design) ----------------------------------------
BP_T, BP_W = 1.5, 3.5          # backplate thickness off the wall x width
AXIS_OFF = 1.5                 # pivot axis in front of the backplate face
KN_H = 1.5                     # knuckle block height (grain runs side to side, along the wall)
KN_FRONT = 1.0                 # wood in front of the pivot hole
KN_P = AXIS_OFF + KN_FRONT     # knuckle projection from the backplate face
BP_MARGIN = 1.5                # backplate beyond each knuckle (wall screws go here)

# ---- swinging swoop (design) ------------------------------------------------
LEG_T, LEG_D, LEG_L = 1.5, 2.0, 10.0   # leg: thickness (along the wall) x depth x length
GAP_TOP = 0.125                # leg top to the top knuckle
WASHER = 0.125                 # nylon bearing washer under the leg
ARM_X1 = LEG_D / 2             # arm root is glued to the leg's outer face
ARM_TIP = 15.0                 # arm tip, out from the axis
ROOT_D = 6.0                   # arm root depth on the leg face (Domino'd)
ARM_D = 2.0                    # arm depth along the level tip
RISE = 2.25                    # top of the swoop rises this much above the leg top
S_X0, S_X1 = 2.5, 10.0         # top S runs between these (level before: clears the knuckle)
EYE_R = 13.0                   # chain point, out from the axis (on the level tip)
UNDER_ANGLE = 60.0             # underside leaves the leg face at this angle from horizontal
K1, K2 = 3.0, 3.0              # underside Bezier handle lengths (shape of the swoop)
DOMINO_Y = (-1.75, -3.25, -4.75) # 8x40 Dominos, arm root to leg

# ---- hardware (design) ------------------------------------------------------
PIN_D = 0.375                  # shoulder diameter of the two shoulder bolts
BOLT_L = 2.0                   # shoulder length
INSERT_D, INSERT_L = 0.5, 0.75 # 5/16-18 insert hole in each leg end
INTO_LEG = BOLT_L - KN_H - WASHER - 0.125   # shoulder enters the leg this far (0.25)

# ---- load (design) ----------------------------------------------------------
DESIGN_LOAD = 30.0
CHAIN_SHOWN = 8.0
POT_SKETCH = (9.0, 6.5)

DOM_8 = (8 / 25.4, 22 / 25.4)

EXTRA = """
<style>
  .wall{fill:url(#wallh);stroke:#555;stroke-width:1}
  .post{fill:#dcb988;stroke:#4a3320;stroke-width:1.3}
  .arm{fill:#ecd2ac;stroke:#4a3320;stroke-width:1.3;stroke-linejoin:round}
  .dom{fill:#f6e7a8;stroke:#8a6d1c;stroke-width:1;stroke-dasharray:3 2}
  .metal{fill:#9a9a9a;stroke:#444;stroke-width:1}
  .brass{fill:#c9a85a;stroke:#5c4a1e;stroke-width:1}
  .nylon{fill:#f4f4f4;stroke:#666;stroke-width:1}
  .pot{fill:#eeeeea;stroke:#888;stroke-width:1;stroke-dasharray:4 3}
  .axis{stroke:#b0452b;stroke-width:1;stroke-dasharray:8 3 2 3;fill:none}
  .swing{fill:none;stroke:#1f5fa8;stroke-width:1;stroke-dasharray:5 4}
  .ghost{fill:#ecd2ac;fill-opacity:.35;stroke:#4a3320;stroke-opacity:.5;stroke-width:1}
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

BP_FACE = -AXIS_OFF                       # backplate front face, x
KN_TOP = (GAP_TOP, GAP_TOP + KN_H)        # top knuckle, y range
KN_BOT = (-LEG_L - WASHER - KN_H, -LEG_L - WASHER)
BP_TOP = KN_TOP[1] + BP_MARGIN
BP_BOT = KN_BOT[0] - BP_MARGIN
SCREW_Y = (KN_TOP[1] + BP_MARGIN / 2, KN_BOT[0] - BP_MARGIN / 2)


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
    p0 = (ARM_X1, -ROOT_D)
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
    """Arm piece profile (x from the leg face to the tip), y up."""
    xs = [ARM_X1, S_X0] + [S_X0 + (S_X1 - S_X0) * i / n for i in range(1, n + 1)] + [ARM_TIP]
    top = [(x, top_y(x)) for x in xs]
    bottom = [(ARM_TIP, RISE - ARM_D), (S_X1, RISE - ARM_D)] + list(reversed(under_pts(n)))
    return top + bottom


def swing_limit_deg():
    """Swing each way from straight out (degrees) before the arm touches something:
    its side against the backplate's front corner, or its tip corner against the wall."""
    corner = 90 + math.degrees(math.asin(min(1.0, (AXIS_OFF - LEG_T / 2) / (BP_W / 2))))
    behind = AXIS_OFF + BP_T                       # wall plane behind the axis
    # tip corner at angle 90+t: distance behind the axis = ARM_TIP*sin t + (LEG_T/2)*cos t
    t = 0.0
    while ARM_TIP * math.sin(math.radians(t)) + LEG_T / 2 * math.cos(math.radians(t)) < behind:
        t += 0.1
    return min(corner, 90 + t)


def planter_limit_deg(dia=None):
    """Swing each way before a hanging planter of this diameter touches the wall."""
    r = (dia or POT_SKETCH[0]) / 2
    behind = AXIS_OFF + BP_T
    c = (r - behind) / EYE_R                       # centre must stay r in front of the wall
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def knuckle_reach():
    """Farthest knuckle corner from the axis (the arm must stay below the knuckle inside this)."""
    return max(math.hypot(BP_W / 2, AXIS_OFF), math.hypot(BP_W / 2, KN_FRONT))


def loads():
    pin_span = (sum(KN_TOP) - sum(KN_BOT)) / 2              # knuckle centre to centre
    couple = DESIGN_LOAD * EYE_R / pin_span                  # horizontal force at each pin
    root_m = DESIGN_LOAD * (EYE_R - ARM_X1)
    dom_lever = max(DOMINO_Y) + ROOT_D                       # top Domino above the root's bearing edge
    dom_t = root_m / dom_lever
    m_wall = DESIGN_LOAD * (EYE_R + AXIS_OFF + BP_T)
    withdraw = m_wall / (SCREW_Y[0] - BP_BOT)
    leg_s = LEG_T * LEG_D ** 2 / 6
    return dict(pin_span=pin_span, couple=couple, root_m=root_m, dom_t=dom_t, m_wall=m_wall,
                withdraw=withdraw, leg_stress=DESIGN_LOAD * EYE_R / leg_s)


def fit_check():
    probs = []
    half_diag = math.hypot(LEG_T / 2, LEG_D / 2)
    if half_diag > AXIS_OFF - 0.125:
        probs.append(f"leg corners ({half_diag:.2f}) hit the backplate face ({AXIS_OFF}) when it turns")
    if S_X0 < knuckle_reach():
        probs.append(f"S starts at {S_X0} but the knuckle reaches {knuckle_reach():.2f} from the axis")
    if EYE_R - 0.5 < S_X1 or EYE_R + 0.75 > ARM_TIP:
        probs.append("eye bolt must sit on the level tip")
    depths = [top_y(x) - under_y(x) for x in [ARM_X1 + 0.1 * i for i in range(int((ARM_TIP - ARM_X1) * 10))]]
    if min(depths) < ARM_D - 0.02:
        probs.append(f"arm thins to {min(depths):.2f} somewhere (want >= {ARM_D})")
    if INTO_LEG < 0.2:
        probs.append("shoulder bolt too short to enter the leg")
    if min(DOMINO_Y) - DOM_8[1] / 2 < -ROOT_D + 0.5:
        probs.append("lowest Domino too close to the root's bottom edge")
    if max(DOMINO_Y) + DOM_8[1] / 2 > -(INSERT_L + INTO_LEG) - 0.25:
        probs.append("top Domino runs into the top insert")
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
    d = Drawing(1120, int((BP_TOP + bot) * s) + 200, 400, 100 + BP_TOP * s, s=s)
    d.text(20, 26, f"Side elevation, swing-arm plant hanger — 1 in = {s} px", "h", "start")
    d.rect(BP_FACE - BP_T - 0.9, -BP_TOP - 1, BP_FACE - BP_T, bot, "wall")
    d.rect(BP_FACE - BP_T, -BP_TOP, BP_FACE, -BP_BOT, "post")
    for sy in SCREW_Y:
        d.add(f'<circle class="metal" cx="{d.x(BP_FACE - BP_T / 2):.1f}" cy="{d.y(-sy):.1f}" r="4.5"/>')
    for y0, y1 in (KN_TOP, KN_BOT):
        d.rect(BP_FACE, -y1, BP_FACE + KN_P, -y0, "post")
    # swoop: leg + arm
    d.rect(-LEG_D / 2, 0, LEG_D / 2, LEG_L, "post")
    d.poly(P(arm_outline()), "arm")
    for yc in DOMINO_Y:
        d.rect(ARM_X1 - 0.79, -yc - DOM_8[1] / 2, ARM_X1 + 0.79, -yc + DOM_8[1] / 2, "dom")
    # pivot hardware (hidden inside the wood: dashed outlines)
    for top in (True, False):
        if top:
            hy = -KN_TOP[1] - 0.25                         # head above the top knuckle
            sy0, sy1 = -KN_TOP[1] - 0.125 + 0.125, -KN_TOP[1] + BOLT_L
            iy0 = INTO_LEG
        else:
            hy = -KN_BOT[0] + 0.125
            sy0, sy1 = -KN_BOT[0] + 0.125 - BOLT_L, -KN_BOT[0] + 0.125
            iy0 = LEG_L - INTO_LEG - INSERT_L
        d.rect(-0.28, hy, 0.28, hy + 0.25, "metal")
        d.add(f'<rect class="hid" x="{d.x(-PIN_D/2):.1f}" y="{d.y(min(sy0, sy1)):.1f}" width="{PIN_D*s:.1f}" height="{abs(sy1-sy0)*s:.1f}"/>')
        d.add(f'<rect class="hid" x="{d.x(-INSERT_D/2):.1f}" y="{d.y(iy0):.1f}" width="{INSERT_D*s:.1f}" height="{INSERT_L*s:.1f}"/>')
    d.rect(-0.5, LEG_L, 0.5, LEG_L + WASHER, "nylon")
    d.line(0, -BP_TOP + 0.6, 0, -BP_BOT - 0.6, "axis")
    # eye bolt, chain, planter
    ty = -RISE
    d.rect(EYE_R - 0.125, ty - 0.2, EYE_R + 0.125, ty + ARM_D + 0.35, "metal")
    d.rect(EYE_R - 0.5, ty - 0.2, EYE_R + 0.5, ty, "metal")
    ey = ty + ARM_D + 0.7
    d.add(f'<circle cx="{d.x(EYE_R):.1f}" cy="{d.y(ey):.1f}" r="{0.45*s:.1f}" fill="none" stroke="#444" stroke-width="2.5"/>')
    yy, i = ty + ARM_D + 1.25, 0
    while yy < pot_top - 0.1:
        w = 0.32 if i % 2 == 0 else 0.12
        d.add(f'<ellipse cx="{d.x(EYE_R):.1f}" cy="{d.y(yy + 0.35):.1f}" rx="{w*s:.1f}" ry="{0.4*s:.1f}" fill="none" stroke="#444" stroke-width="1.8"/>')
        yy += 0.6
        i += 1
    pd, ph = POT_SKETCH
    for dx in (-pd / 2 + 0.5, pd / 2 - 0.5):
        d.line(EYE_R, pot_top, EYE_R + dx, pot_top + 1.8, "pot")
    d.poly([(EYE_R - pd / 2, pot_top + 1.8), (EYE_R + pd / 2, pot_top + 1.8),
            (EYE_R + pd / 2 - 1, pot_top + ph), (EYE_R - pd / 2 + 1, pot_top + ph)], "pot")
    # dims
    d.dim_h(BP_FACE - BP_T, ARM_TIP, 52, f"{frac(ARM_TIP - BP_FACE + BP_T)} off the wall", pyo=d.y(-BP_TOP))
    d.dim_h(BP_FACE, EYE_R, 76, f"{frac(EYE_R - BP_FACE)} from the backplate to the chain", pyo=d.y(-RISE))
    d.dim_v(-BP_TOP, -BP_BOT, d.x(BP_FACE - BP_T) - 44, f"backplate {frac(BP_TOP - BP_BOT)}", pxo=d.x(BP_FACE - BP_T))
    d.dim_v_text(-RISE, -RISE + ARM_D, d.x(ARM_TIP) + 14, f"{frac(ARM_D)} deep at the tip", pxo=d.x(ARM_TIP))
    d.dim_v_text(0, ROOT_D, d.x(ARM_X1) + 3.6 * s, f"root {frac(ROOT_D)}", pxo=d.x(ARM_X1) + 1.2 * s, side="right")
    # callouts
    lx = d.x(max(ARM_TIP, EYE_R + POT_SKETCH[0] / 2)) + 22
    L = lambda fx, fy, ly, txt: d.leader(d.x(fx), d.y(fy), lx, ly, txt)
    L(EYE_R, ty + 0.4, d.y(ty) + 44, "¼-20 forged eye bolt")
    L(EYE_R + 0.3, ty + ARM_D + 4, d.y(ty) + 74, "rated chain + quick link, WLL ≥ 60 lb")
    L(EYE_R + pd / 2 - 0.6, pot_top + ph / 2, d.y(pot_top + ph / 2), f"planter, for scale (≤ {DESIGN_LOAD:.0f} lb wet)")
    L(ARM_X1 + 0.4, -DOMINO_Y[1], d.y(ty) + 104, "3 × 8×40 Domino, arm root → leg")
    L(4.5, -top_y(4.5) + 0.4, d.y(ty) + 134, "arm: grain horizontal")
    lxl = d.x(BP_FACE - BP_T) - 70
    LL = lambda fx, fy, ly, txt: d.leader(d.x(fx), d.y(fy), lxl, ly, txt, "end")
    LL(0, -KN_TOP[1] - 0.15, d.y(-KN_TOP[1]) - 22, "⅜″ shoulder bolt = pivot pin")
    LL(BP_FACE + 0.3, -sum(KN_TOP) / 2, d.y(-KN_TOP[1]) + 6, "top knuckle (Domino + screws)")
    LL(-0.3, 5.0, d.y(5.0), "leg: grain vertical, 1½ × 2 × 10")
    LL(0.2, LEG_L + WASHER / 2, d.y(LEG_L) + 22, "nylon bearing washer")
    LL(BP_FACE + 0.3, -sum(KN_BOT) / 2, d.y(-KN_BOT[0]) + 30, "bottom knuckle, bolt from below")
    LL(BP_FACE - BP_T / 2, -SCREW_Y[0], d.y(-SCREW_Y[0]) - 40, "wall screw into a stud (2)")
    yb = d.y(bot) + 28
    d.text(20, yb, "Red dash-dot = pivot axis. Yellow dashed = Dominos. Grey dashed = bolts and inserts inside the wood; planter for scale.", "n", "start")
    d.text(20, yb + 16, f"Leg {frac(LEG_L)} long; knuckles {frac(KN_H)} tall, projecting {frac(KN_P)}; axis {frac(AXIS_OFF)} in front of the backplate. "
           f"Wall screws {frac(BP_MARGIN / 2)} beyond each knuckle.", "n", "start")
    d.save(path, "Swing-arm plant hanger, side elevation", EXTRA)


def plan_and_pivot(path):
    s = 16
    d = Drawing(1120, 620, 330, 90, s=s)
    d.text(20, 26, f"Plan (from above): swing range — 1 in = {s} px", "h", "start")
    # wall along the top; y = out from the wall; axis at y = BP_T + AXIS_OFF
    ay = BP_T + AXIS_OFF
    d.rect(-17, -0.8, 17, 0, "wall")
    d.rect(-BP_W / 2, 0, BP_W / 2, BP_T, "post")
    d.rect(-BP_W / 2, BP_T, BP_W / 2, BP_T + KN_P, "post")
    lim = swing_limit_deg()
    plim = planter_limit_deg()

    def arm_rect(theta, cls):
        c, sn = math.cos(math.radians(theta)), math.sin(math.radians(theta))
        pts = []
        for (u, v) in [(-LEG_D / 2, -LEG_T / 2), (ARM_TIP, -LEG_T / 2), (ARM_TIP, LEG_T / 2), (-LEG_D / 2, LEG_T / 2)]:
            # u along the arm (0° = straight out from the wall), v across it
            pts.append((u * sn + v * c, ay + u * c - v * sn))
        d.poly(pts, cls)
    for th in (-90, 90):
        arm_rect(th, "ghost")
    arm_rect(0, "arm")
    d.add(f'<circle class="pot" cx="{d.x(0):.1f}" cy="{d.y(ay + EYE_R):.1f}" r="{POT_SKETCH[0]/2*s:.1f}"/>')
    # swing arc for the eye
    a0, a1 = -lim, lim
    pts = [(EYE_R * math.sin(math.radians(a)), ay + EYE_R * math.cos(math.radians(a)))
           for a in [a0 + (a1 - a0) * i / 60 for i in range(61)]]
    d.add('<polyline class="swing" points="' + ' '.join(f'{d.x(x):.1f},{d.y(y):.1f}' for x, y in pts) + '"/>')
    d.add(f'<circle class="metal" cx="{d.x(0):.1f}" cy="{d.y(ay):.1f}" r="{PIN_D/2*s:.1f}"/>')
    d.text(d.x(0), d.y(ay + EYE_R) + 4, "planter", "n")
    d.text(d.x(0), d.y(ay + EYE_R + POT_SKETCH[0] / 2) + 22,
           f"Arm swings ±{lim:.0f}° before its tip meets the wall; a {frac(POT_SKETCH[0])} planter touches the wall at about ±{plim:.0f}°.", "n")
    d.text(d.x(0), d.y(ay + EYE_R + POT_SKETCH[0] / 2) + 38,
           "Ghosted: the arm swung flat along the wall each way (dashed arc = path of the chain).", "n")
    d.dim_h(-BP_W / 2, BP_W / 2, d.y(0) - 12, frac(BP_W), pyo=d.y(0))
    d.leader(d.x(-BP_W / 2), d.y(BP_T + KN_P / 2), d.x(-BP_W / 2) - 60, d.y(BP_T + KN_P / 2) + 60,
             "knuckle (grain along the wall)", "end")
    # ---- pivot section detail (right) ----
    ps = 40
    c = Drawing(1120, 620, 820, 150, s=ps)
    c.text(700, 126, f"Pivot section through the axis — 1 in = {ps} px", "t", "start")
    # top knuckle + leg top
    c.rect(-1.2, 0, 1.2, KN_H, "post")
    c.rect(-LEG_D / 2, KN_H + GAP_TOP, LEG_D / 2, KN_H + GAP_TOP + 2.2, "post")
    c.rect(-0.28, -0.25, 0.28, 0, "metal")                              # head (⅛″ above the knuckle when seated)
    c.rect(-PIN_D / 2, 0, PIN_D / 2, KN_H + GAP_TOP + INTO_LEG, "metal")
    c.rect(-0.156, KN_H + GAP_TOP + INTO_LEG, 0.156, KN_H + GAP_TOP + INTO_LEG + 0.5, "metal")
    c.rect(-INSERT_D / 2, KN_H + GAP_TOP + INTO_LEG, -0.156, KN_H + GAP_TOP + INTO_LEG + INSERT_L, "brass")
    c.rect(0.156, KN_H + GAP_TOP + INTO_LEG, INSERT_D / 2, KN_H + GAP_TOP + INTO_LEG + INSERT_L, "brass")
    c.line(0, -0.6, 0, KN_H + GAP_TOP + 2.4, "axis")
    notes = [f"⅜″ × {frac(BOLT_L)} shoulder bolt, 5/16-18 thread", "turns in a ⅜″ hole in the knuckle",
             f"shoulder enters the leg {frac(INTO_LEG)}", "5/16-18 insert in the leg end (end grain)",
             f"{frac(GAP_TOP)} gap leg → knuckle (bottom: nylon washer)"]
    for k, t in enumerate(notes):
        c.text(c.x(1.6), c.y(0.1 + 0.42 * k) + 4, t, "n", "start")
    c.text(700, c.y(KN_H + GAP_TOP + 2.2) + 26, "Bottom pivot is the same, upside down, with the leg resting", "n", "start")
    c.text(700, c.y(KN_H + GAP_TOP + 2.2) + 42, "on the washer. Tighten both bolts into the inserts; the", "n", "start")
    c.text(700, c.y(KN_H + GAP_TOP + 2.2) + 58, "shoulders turn in the knuckles and the heads stop it lifting off.", "n", "start")
    d.p.extend(c.p)
    d.save(path, "Swing-arm plant hanger, plan and pivot detail", EXTRA)


def templates(path):
    s = 34
    yoff = RISE
    d = Drawing(1080, 700, 60, 90 + yoff * s, s=s)
    d.text(20, 26, f"Band-saw template — arm, 1 in = {s} px; grid = 1″ (print, then check one grid square)", "h", "start")
    x0 = ARM_X1
    rel = [(x - x0, -y) for x, y in arm_outline(60)]
    d.poly(rel, "tmpl")
    for i in range(0, math.ceil(ARM_TIP - x0) + 1):
        d.line(i, -math.ceil(RISE), i, ROOT_D, "grid5" if i % 5 == 0 else "grid")
    for j in range(-math.ceil(RISE), int(ROOT_D) + 1):
        d.line(0, j, ARM_TIP - x0, j, "grid5" if j % 5 == 0 else "grid")
    d.add('<polygon fill="none" stroke="#2b1a0f" stroke-width="1.8" points="' +
          ' '.join(f'{d.x(a):.1f},{d.y(b):.1f}' for a, b in rel) + '"/>')
    for yc in DOMINO_Y:
        d.rect(0, -yc - DOM_8[1] / 2, 0.79, -yc + DOM_8[1] / 2, "dom")
    d.line(EYE_R - x0, -RISE - 0.2, EYE_R - x0, -RISE + ARM_D + 0.2, "axis")
    d.text(d.x(EYE_R - x0), d.y(-RISE + ARM_D) + 16, "eye", "n")
    for xk in (S_X0, S_X1):
        d.line(xk - x0, -top_y(xk) - 0.35, xk - x0, -top_y(xk) + 0.35, "axis")
    d.text(d.x(0) + 6, d.y(0) - 6, "root end (glues to the leg)", "n", "start")
    d.dim_v(0, ROOT_D, d.x(0) - 14, frac(ROOT_D), pxo=d.x(0))
    d.dim_v_text(-RISE, -RISE + ARM_D, d.x(ARM_TIP - x0) + 12, frac(ARM_D), pxo=d.x(ARM_TIP - x0))
    d.dim_h(0, ARM_TIP - x0, d.y(ROOT_D) + 26, f"{frac(ARM_TIP - x0)}", pyo=d.y(ROOT_D), below=True)
    d.text(d.x(0), d.y(ROOT_D) + 64,
           f"ARM (cut 1) — blank {frac(LEG_T)} × {frac(ROOT_D + RISE)} × {frac(ARM_TIP - x0 + 0.5)}, grain along the length. "
           f"Top: level for {frac(S_X0 - x0)}, then an S rising {frac(RISE)} to {frac(S_X1 - x0)}, level to the tip.", "n", "start")
    d.text(d.x(0), d.y(ROOT_D) + 80,
           f"Underside: leaves the root's bottom corner at {UNDER_ANGLE:.0f}° and sweeps into the level tip at {frac(S_X1 - x0)}.",
           "n", "start")
    d.text(d.x(0), d.y(ROOT_D) + 96, "Plot both edges from the ordinate tables on the plan page and bend a thin batten through the points.", "n", "start")
    d.save(path, "Swing-arm plant hanger, band-saw template for the arm", EXTRA)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "..", "static", "static", "woodworking")
    os.makedirs(out, exist_ok=True)
    probs = fit_check()
    for p in probs:
        print("FIT:", p)
    if probs:
        raise SystemExit(1)
    side(os.path.join(out, "swing-arm-hanger-side.svg"))
    plan_and_pivot(os.path.join(out, "swing-arm-hanger-plan.svg"))
    templates(os.path.join(out, "swing-arm-hanger-templates.svg"))
    L = loads()
    print(f"backplate {BP_TOP - BP_BOT:.3f} tall; knuckles at y {KN_TOP} and {KN_BOT}; screws at {SCREW_Y}")
    print(f"off the wall {ARM_TIP + AXIS_OFF + BP_T:.2f}; backplate face to chain {EYE_R + AXIS_OFF:.2f}")
    print("top ordinates (from leg face):", ", ".join(f"{x - ARM_X1:g}:{top_y(x):.2f}" for x in [2.5, 4, 5, 6, 7, 8, 9, 10]))
    print("underside ordinates (from leg face):", ", ".join(f"{x - ARM_X1:g}:{under_y(x):.2f}" for x in [1.25, 1.5, 2, 3, 4, 5, 6, 7, 8, 9]))
    print("depth min:", f"{min(top_y(x) - under_y(x) for x in [ARM_X1 + 0.1 * i for i in range(140)]):.2f}")
    print(f"swing limit ±{swing_limit_deg():.0f}° (9in planter ±{planter_limit_deg():.0f}°, 12in ±{planter_limit_deg(12):.0f}°), knuckle reach {knuckle_reach():.2f}, into leg {INTO_LEG}")
    print(f"pin span {L['pin_span']:.2f}, pin couple {L['couple']:.0f} lb, root moment {L['root_m']:.0f} in-lb, "
          f"top Domino tension ≈ {L['dom_t']:.0f} lb, wall moment {L['m_wall']:.0f} in-lb, top screw ≈ {L['withdraw']:.0f} lb, "
          f"leg bending ≈ {L['leg_stress']:.0f} psi")
    print("wrote 3 SVGs to", os.path.normpath(out))
