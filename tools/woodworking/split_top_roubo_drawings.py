#!/usr/bin/env python3
"""Drawings for the split-top Roubo bench that doubles as a table-saw outfeed table
(Benchcrafted-style: Glide leg vise on a Crisscross Retro, plus a tail vise).

Usage: python3 tools/woodworking/split_top_roubo_drawings.py
Writes static/static/woodworking/roubo-*.svg
Inches throughout. x runs along the bench: 0 = the SAW END (flat, no hardware), 87 = the tail-vise end.
y runs back (0) to front (24). z is height above the floor. Edit the constants and re-run;
the cut-list numbers printed at the end come from the same constants.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from modern_craftsman_drawings import Drawing

_G = {1: "1/16", 2: "⅛", 3: "3/16", 4: "¼", 5: "5/16", 6: "⅜", 7: "7/16", 8: "½",
      9: "9/16", 10: "⅝", 11: "11/16", 12: "¾", 13: "13/16", 14: "⅞", 15: "15/16"}


def frac(v):
    """Inches -> 11-3/16″ style label (hyphen between whole and a plain fraction)."""
    whole, rem = divmod(round(v * 16), 16)
    if rem == 0:
        return f"{whole}″"
    g = _G[rem]
    if not whole:
        return g + "″"
    return f"{whole}{'-' if '/' in g else ''}{g}″"


OUT = os.path.join(os.path.dirname(__file__), "..", "..", "static", "static", "woodworking")

# ---- from the Benchcrafted split-top preview drawings (stated) --------------
L, W = 87.0, 24.0                 # overall
TOP_T = 4.0                       # top thickness
TOP_H = 35.0                      # finished top height; chop is 34½″ tall, ½″ off the floor
SLAB = 11 + 3 / 16                # each top slab's width (11-3/16)
GAP = W - 2 * SLAB                # 1⅝″ between the slabs
LEG_W, LEG_T = 5 + 3 / 8, 3.5     # leg: 5⅜″ across the front, 3½″ deep
LEG_OVH_L = 14.75                 # saw-end overhang, to the leg-vise leg's face
BETWEEN = 41 + 5 / 8              # between the front legs
LEG_OVH_R = 19 + 7 / 8            # tail-end overhang
SHELF_LOW = 5.0                   # underside of the lower rails above the floor
CHOP_H, CHOP_Z0 = 34.5, 0.5

# ---- chosen / estimated by me ------------------------------------------------
FOOT = 0.5                        # leveling-foot allowance (±⅜″ travel) under each leg (chosen)
LEG_LEN = TOP_H - TOP_T - FOOT    # 30½  (derived)
CHOP_T = 2.5                      # chop thickness (est.; the vise manual governs)
CHOP_BOT_W = 3.75                 # chop width at the floor; tapers from 5⅜″ at the top (est. from the preview)
SCREW_DROP = 14.5                 # leg-vise screw axis below the benchtop (est. from the preview)
CRISS_TOP, CRISS_LEN = 16.0, 18.0 # Crisscross mortise: starts this far below the top, 18″ long (V2)
WHEEL_R = 5.0
RAIL_H = 3.5                      # short and long rails (est.)
RAIL_Z0 = SHELF_LOW               # lower rails 5″–8½″
DEAD_X0, DEAD_W = 51.4, 7.6       # deadman (est. from the preview)
SAW_GAP = 0.25                    # air between bench end and saw table
SAW_TABLE_D = 27.0                # a generic cabinet-saw table, front to back (use yours)
SAW_TABLE_THK = 1.5

# tail vise (hardware = Benchcrafted Tail Vise; layout below is est., the template governs)
CAP_T = 3.0                       # end cap thickness (the guide recommends 3″)
SLAB_L = L - CAP_T                # slabs run 84″
SCREW_LEN = 18.0
TRAVEL = 12.25                    # one reseller's figure for a 2⅞″ cap; verify
DOG = 0.75
DOG_PITCH = 5.0                   # est. from the preview (≈4.9″)
DOG_X0 = 12.0
DOG_N = 14
LAM, STRIP, BACK = 1.75, 1.5, 0.75          # front laminate, dog strip, backing strip (est.)
MAIN = SLAB - LAM - STRIP - BACK            # 7 3/16
DOG_FRONT0, DOG_FRONT1 = LAM + STRIP - DOG, LAM + STRIP   # notch, measured from the front: 2½″ .. 3¼″
SCREW_FROM_FRONT = 5.5
BLOCK_L = 5.0                     # dog block
# gap bridge
LEDGE_W, LEDGE_H, LEDGE_DROP = 3 / 8, 3 / 4, 3 / 4
BRIDGE_W = GAP - 1 / 16           # 1 9/16
BRIDGE_T = LEDGE_DROP

EXTRA = """
<style>
  .chop{fill:#cfa972;stroke:#4a3320;stroke-width:1.3;stroke-linejoin:round}
  .cap{fill:#c99a63;stroke:#4a3320;stroke-width:1.3}
  .ghost{fill:#eef1f4;fill-opacity:.7;stroke:#6b7885;stroke-width:1.2;stroke-dasharray:6 4}
  .metal{fill:#d9dde1;stroke:#4a525a;stroke-width:1.2}
  .scr{stroke:#4a525a;stroke-width:3}
  .hole{fill:#fff;stroke:#4a3320;stroke-width:1}
  .dead{fill:#e6c79c;stroke:#4a3320;stroke-width:1.3}
  .outl{fill:none;stroke:#7a6a5a;stroke-width:1.2;stroke-dasharray:5 3}
  .gapc{fill:#fff;stroke:#4a3320;stroke-width:1.1;stroke-dasharray:5 3}
  .bridge{fill:#f3dfbf;stroke:#b0452b;stroke-width:1.4}
  .arrow{stroke:#b0452b;stroke-width:2;fill:none;marker-end:url(#r)}
  .red{font:600 12px 'Helvetica Neue',Arial,sans-serif;fill:#b0452b}
  .plate{fill:#b9c0c7;stroke:#4a525a;stroke-width:1.2}
</style>
<defs>
  <marker id="r" viewBox="0 0 8 8" refX="8" refY="4" markerWidth="8" markerHeight="8" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="#b0452b"/>
  </marker>
</defs>
"""

LEGS_X = [LEG_OVH_L, LEG_OVH_L + LEG_W + BETWEEN]       # left faces of the two leg pairs
assert abs(LEG_OVH_L + 2 * LEG_W + BETWEEN + LEG_OVH_R - L) < 1e-9
assert abs(MAIN + BACK + STRIP + LAM - SLAB) < 1e-9
CHOP_CX = LEGS_X[0] + LEG_W / 2


def circle(d, cx, cy, r, cls):
    d.add(f'<circle class="{cls}" cx="{d.x(cx):.1f}" cy="{d.y(cy):.1f}" r="{r*d.s:.1f}"/>')


def arrow(d, x1, y1, x2, y2):
    d.add(f'<line class="arrow" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')


# ===========================================================================
# 1. Front elevation, with the saw butted up to the saw end
# ===========================================================================
def front(path):
    S = 8
    ZT = 40.0
    zy = lambda z: ZT - z
    d = Drawing(1180, 470, 330, 60, s=S)
    d.text(20, 26, "Front elevation, with the table saw at the saw end (1 in = 8 px)", "h", "start")
    d.add(f'<line class="floor" x1="{d.x(-40):.1f}" y1="{d.y(zy(0)):.1f}" x2="{d.x(L+16):.1f}" y2="{d.y(zy(0)):.1f}"/>')
    # saw (ghost): table at the bench height, cabinet below
    sx1, sx0 = -SAW_GAP, -SAW_GAP - 36
    d.rect(sx0, zy(TOP_H), sx1, zy(TOP_H - SAW_TABLE_THK), "ghost")
    d.rect(sx0 + 4, zy(TOP_H - SAW_TABLE_THK), sx1 - 5, zy(0.5), "ghost")
    d.text(d.x((sx0 + sx1) / 2), d.y(zy(17)), "YOUR TABLE SAW", "n")
    d.text(d.x((sx0 + sx1) / 2), d.y(zy(17)) + 14, "(raise or lower it to meet", "n")
    d.text(d.x((sx0 + sx1) / 2), d.y(zy(17)) + 27, "the bench top)", "n")
    d.leader(d.x(0), d.y(zy(TOP_H)) - 2, d.x(-9), d.y(zy(TOP_H)) - 26, f"{frac(SAW_GAP)} gap, never touching", "end", "red")
    # base
    for i, lx in enumerate(LEGS_X):
        if i == 0:
            d.rect(lx, zy(CHOP_Z0 + 0.0 + (LEG_LEN)), lx + LEG_W, zy(FOOT), "leg")   # fixed leg behind the chop
        else:
            d.rect(lx, zy(FOOT + LEG_LEN), lx + LEG_W, zy(FOOT), "leg")
        d.rect(lx + LEG_W / 2 - 1.2, zy(FOOT), lx + LEG_W / 2 + 1.2, zy(0), "metal")   # leveling foot
    # rails and deadman
    d.rect(LEGS_X[0] + LEG_W, zy(RAIL_Z0 + RAIL_H), LEGS_X[1], zy(RAIL_Z0), "wood")
    d.rect(DEAD_X0, zy(TOP_H - TOP_T), DEAD_X0 + DEAD_W, zy(RAIL_Z0 + RAIL_H), "dead")
    for col in (DEAD_X0 + DEAD_W * 0.3, DEAD_X0 + DEAD_W * 0.7):
        for k in range(9):
            circle(d, col, zy(TOP_H - TOP_T - 2.2 - 2 * k), 0.375, "hole")
    # top (slabs run to the cap)
    d.rect(0, zy(TOP_H), SLAB_L, zy(TOP_H - TOP_T), "wood")
    d.rect(SLAB_L, zy(TOP_H), L, zy(TOP_H - TOP_T), "cap")
    d.leader(d.x(SLAB_L + CAP_T / 2), d.y(zy(TOP_H)), d.x(SLAB_L - 6), d.y(zy(TOP_H)) - 22, "end cap", "end")
    # tail-vise screw, handwheel
    d.rect(L, zy(TOP_H - 1.4), L + 2, zy(TOP_H - 2.0), "metal")
    d.rect(L + 2, zy(TOP_H - 0.5), L + 3.4, zy(TOP_H - 3.0), "metal")
    d.text(d.x(L + 1.5), d.y(zy(TOP_H)) - 32, "tail-vise", "n")
    d.text(d.x(L + 1.5), d.y(zy(TOP_H)) - 20, "handwheel", "n")
    # chop (tapered), screw axis, wheel, crisscross
    cx = CHOP_CX
    d.poly([(cx - LEG_W / 2, zy(TOP_H)), (cx + LEG_W / 2, zy(TOP_H)),
            (cx + CHOP_BOT_W / 2, zy(CHOP_Z0)), (cx - CHOP_BOT_W / 2, zy(CHOP_Z0))], "chop")
    zc = TOP_H - SCREW_DROP
    d.rect(cx - 1.5, zy(TOP_H - CRISS_TOP - CRISS_LEN), cx + 1.5, zy(TOP_H - CRISS_TOP), "outl")
    circle(d, cx, zy(zc), WHEEL_R, "hole")
    circle(d, cx, zy(zc), 1.3, "metal")
    for a in (-35, 85, 205):
        circle(d, cx + WHEEL_R * math.cos(math.radians(a)), zy(zc) + WHEEL_R * math.sin(math.radians(a)) * -1, 0.55, "metal")
    d.leader(d.x(cx - 2.7), d.y(zy(8)), d.x(cx - 11), d.y(zy(8)) + 24, "Crisscross Retro (18″ mortise)", "end")
    d.leader(d.x(cx - 4.2), d.y(zy(zc)) - 28, d.x(cx - 11), d.y(zy(zc)) - 44, "Glide handwheel", "end")
    d.leader(d.x(cx + 1.2), d.y(zy(34)) , d.x(cx + 3), d.y(zy(TOP_H)) - 42, "chop, 2½″ thick, flush with the top", "start")
    d.text(d.x(DEAD_X0 + DEAD_W / 2), d.y(zy(TOP_H - TOP_T)) + 14, "", "n")
    d.leader(d.x(DEAD_X0 + DEAD_W), d.y(zy(20)), d.x(DEAD_X0 + DEAD_W + 4), d.y(zy(20)) + 0, "deadman", "start")
    # dimensions (below the floor)
    base = d.y(zy(0)) + 24
    d.dim_h(0, LEGS_X[0], base, frac(LEGS_X[0]), d.y(zy(0)))
    d.dim_h(LEGS_X[0], LEGS_X[0] + LEG_W, base, frac(LEG_W), d.y(zy(0)))
    d.dim_h(LEGS_X[0] + LEG_W, LEGS_X[1], base, frac(BETWEEN), d.y(zy(0)))
    d.dim_h(LEGS_X[1], LEGS_X[1] + LEG_W, base, frac(LEG_W), d.y(zy(0)))
    d.dim_h(LEGS_X[1] + LEG_W, L, base, frac(LEG_OVH_R), d.y(zy(0)))
    d.dim_h(0, L, base + 30, frac(L) + " overall", d.y(zy(0)))
    d.dim_v(zy(TOP_H), zy(0), d.x(L + 10), frac(TOP_H) + " top height", d.x(L + 3.5), left=False)
    d.dim_v(zy(TOP_H), zy(TOP_H - TOP_T), d.x(-1.5) - 0, "4″", d.x(0))
    d.dim_v(zy(RAIL_Z0), zy(0), d.x(LEGS_X[0] + LEG_W + 3), frac(RAIL_Z0), d.x(LEGS_X[0] + LEG_W))
    d.save(path, "Split-top Roubo bench, front elevation with the table saw at the saw end", EXTRA)


# ===========================================================================
# 2. Plan
# ===========================================================================
def plan(path):
    S = 8
    d = Drawing(1190, 420, 330, 110, s=S)
    d.text(20, 26, "Plan: saw end on the left, tail-vise end on the right (1 in = 8 px)", "h", "start")
    # saw table (ghost)
    sy0 = W / 2 - SAW_TABLE_D / 2
    d.rect(-SAW_GAP - 40, sy0, -SAW_GAP, sy0 + SAW_TABLE_D, "ghost")
    d.text(d.x(-SAW_GAP - 20), d.y(W / 2) - 20, "YOUR SAW TABLE", "n")
    d.text(d.x(-SAW_GAP - 20), d.y(W / 2) - 6, f"({frac(SAW_TABLE_D)} deep shown; use yours)", "n")
    d.line(-SAW_GAP - 40, W / 2 + 2, L + 12, W / 2 + 2, "ext")
    arrow(d, d.x(4), d.y(W / 2 + 2) - 0, d.x(34), d.y(W / 2 + 2) - 0)
    d.text(d.x(19), d.y(W / 2 + 2) - 10, "rip direction", "red")
    # slabs
    d.rect(0, 0, SLAB_L, SLAB, "wood")
    d.rect(0, SLAB + GAP, SLAB_L, W, "wood")
    d.rect(0, SLAB, SLAB_L, SLAB + GAP, "bridge")
    d.text(d.x(40), d.y(SLAB + GAP / 2) + 4, "gap bridge (drops in flush for outfeed use)", "n")
    # front laminate lines
    for yy in (W - LAM, W - LAM - STRIP, W - LAM - STRIP - BACK):
        d.line(0, yy, SLAB_L, yy, "hid")
    # dog notches
    for k in range(DOG_N):
        x0 = DOG_X0 + k * DOG_PITCH
        d.rect(x0, W - DOG_FRONT1, x0 + DOG, W - DOG_FRONT0, "hole")
    # end cap
    d.rect(SLAB_L, 0, L, W, "cap")
    d.text(d.x(SLAB_L + CAP_T / 2), d.y(6), "end cap", "n")
    # tail vise
    sy = W - SCREW_FROM_FRONT
    d.add(f'<line class="scr" x1="{d.x(SLAB_L - SCREW_LEN):.1f}" y1="{d.y(sy):.1f}" x2="{d.x(L + 1.2):.1f}" y2="{d.y(sy):.1f}"/>')
    d.rect(L + 1.2, sy - 3.2, L + 2.6, sy + 3.2, "metal")
    d.leader(d.x(L + 2), d.y(sy) + 28, d.x(L - 14), d.y(sy) + 58, "tail-vise screw + handwheel", "end")
    # leg vise
    cx = CHOP_CX
    d.rect(cx - LEG_W / 2, W, cx + LEG_W / 2, W + CHOP_T, "chop")
    d.add(f'<line class="scr" x1="{d.x(cx):.1f}" y1="{d.y(W+CHOP_T):.1f}" x2="{d.x(cx):.1f}" y2="{d.y(W+CHOP_T+5):.1f}"/>')
    d.rect(cx - WHEEL_R, W + CHOP_T + 5, cx + WHEEL_R, W + CHOP_T + 6, "metal")
    d.leader(d.x(cx + WHEEL_R), d.y(W + CHOP_T + 5.5), d.x(cx + 9), d.y(W + CHOP_T + 7), "Glide leg vise (shown closed)", "start")
    # hidden legs
    for lx in LEGS_X:
        d.rect(lx, 0, lx + LEG_W, LEG_T, "outl")
        d.rect(lx, W - LEG_T, lx + LEG_W, W, "outl")
    d.rect(DEAD_X0, W - 2.0, DEAD_X0 + DEAD_W, W - 0.75, "outl")
    d.leader(d.x(DEAD_X0 + DEAD_W / 2), d.y(W - 1.4), d.x(DEAD_X0 + DEAD_W / 2 + 4), d.y(W + 5), "deadman (slides in the front rail)", "start")
    # dimensions
    d.dim_h(0, L, d.y(-6), frac(L) + " overall", d.y(0))
    d.text(d.x(-SAW_GAP) - 4, d.y(-4) - 6, f"{frac(SAW_GAP)} air to saw", "red", "end")
    d.dim_v(0, SLAB, d.x(-4), frac(SLAB), d.x(0))
    d.dim_v(SLAB, SLAB + GAP, d.x(-9) - 0, "", d.x(0))
    d.leader(d.x(-9), d.y(SLAB + GAP / 2), d.x(-16), d.y(SLAB + GAP / 2) + 22, f"{frac(GAP)} gap", "end")
    d.dim_v(SLAB + GAP, W, d.x(-4), frac(SLAB), d.x(0))
    d.leader(d.x(DOG_X0 + 6 * DOG_PITCH + 0.4), d.y(W - 2.8), d.x(DOG_X0 + 6 * DOG_PITCH) - 20, d.y(W) + 36, f"¾″ square dog notches, ~{frac(DOG_PITCH)} pitch (est.)", "middle")
    d.dim_h(SLAB_L, L, d.y(W) + 22, f"cap {frac(CAP_T)}", d.y(W))
    d.save(path, "Split-top Roubo bench, plan, with saw table, vises, dog row and gap bridge", EXTRA)


# ===========================================================================
# 3. End elevation, from the saw end
# ===========================================================================
def end(path):
    S = 14
    ZT = 37.0
    zy = lambda z: ZT - z
    d = Drawing(780, 650, 140, 60, s=S)
    d.text(20, 26, "End elevation, looking from the saw end (1 in = 14 px)", "h", "start")
    d.add(f'<line class="floor" x1="{d.x(-8):.1f}" y1="{d.y(zy(0)):.1f}" x2="{d.x(W+16):.1f}" y2="{d.y(zy(0)):.1f}"/>')
    # top + gap
    d.rect(0, zy(TOP_H), SLAB, zy(TOP_H - TOP_T), "wood")
    d.rect(SLAB + GAP, zy(TOP_H), W, zy(TOP_H - TOP_T), "wood")
    # legs (cut by the section line: shown whole)
    for y0 in (0, W - LEG_T):
        d.rect(y0, zy(FOOT + LEG_LEN), y0 + LEG_T, zy(FOOT), "leg")
        d.rect(y0 + LEG_T / 2 - 0.6, zy(FOOT), y0 + LEG_T / 2 + 0.6, zy(0), "metal")
    # short rails, upper and lower
    for z0 in (TOP_H - TOP_T - RAIL_H, RAIL_Z0):
        d.rect(LEG_T, zy(z0 + RAIL_H), W - LEG_T, zy(z0), "wood")
    # shelf boards
    d.rect(LEG_T, zy(RAIL_Z0 + RAIL_H + 0.75), W - LEG_T, zy(RAIL_Z0 + RAIL_H), "face")
    d.text(d.x(W / 2), d.y(zy(RAIL_Z0 + RAIL_H)) - 14, "shelf boards", "n")
    # chop, screw, wheel
    d.rect(W, zy(CHOP_Z0 + CHOP_H), W + CHOP_T, zy(CHOP_Z0), "chop")
    zc = TOP_H - SCREW_DROP
    d.add(f'<line class="scr" x1="{d.x(W - 1):.1f}" y1="{d.y(zy(zc)):.1f}" x2="{d.x(W + CHOP_T + 5.5):.1f}" y2="{d.y(zy(zc)):.1f}"/>')
    d.rect(W + CHOP_T + 5.5, zy(zc + WHEEL_R), W + CHOP_T + 6.7, zy(zc - WHEEL_R), "metal")
    d.rect(W - 0.2, zy(TOP_H - CRISS_TOP - CRISS_LEN), W + CHOP_T + 0.2, zy(TOP_H - CRISS_TOP), "outl")
    d.text(d.x(W + CHOP_T + 3), d.y(zy(8)), "Crisscross arms", "n")
    d.text(d.x(W + CHOP_T + 3), d.y(zy(8)) + 13, "in the chop and leg", "n")
    d.leader(d.x(W + CHOP_T / 2), d.y(zy(TOP_H)) + 4, d.x(W + 6), d.y(zy(TOP_H)) - 22, "chop, 2½″ (est.)", "start")
    d.text(d.x(W / 2), d.y(zy(TOP_H)) - 12, "the saw end is plain: no hardware, no chamfer", "n")
    # dimensions
    d.dim_h(0, W, d.y(zy(0)) + 26, frac(W), d.y(zy(0)))
    d.dim_h(0, LEG_T, d.y(zy(0)) + 52, frac(LEG_T), d.y(zy(0)))
    d.dim_h(LEG_T, W - LEG_T, d.y(zy(0)) + 52, frac(W - 2 * LEG_T), d.y(zy(0)))
    d.dim_h(W - LEG_T, W, d.y(zy(0)) + 52, frac(LEG_T), d.y(zy(0)))
    d.dim_v(zy(TOP_H), zy(0), d.x(-3), frac(TOP_H), d.x(0))
    d.dim_v(zy(TOP_H), zy(TOP_H - TOP_T), d.x(-3) + 0, "", d.x(0)) if False else None
    d.dim_v(zy(FOOT), zy(0), d.x(W - LEG_T) - 26, "", d.x(W - LEG_T))
    d.leader(d.x(W - LEG_T - 1.5), d.y(zy(FOOT / 2)), d.x(W - 6), d.y(zy(FOOT / 2)) + 82, f"{frac(FOOT)} leveling feet, ±⅜″", "end")
    d.save(path, "Split-top Roubo bench, end elevation from the saw end", EXTRA)


# ===========================================================================
# 4. Top cross-section: slabs, gap bridge, front build-up
# ===========================================================================
def section(path):
    S = 30
    d = Drawing(1000, 400, 90, 80, s=S)
    d.text(20, 26, "Top cross-section: slab build-up and gap bridge (1 in = 30 px)", "h", "start")
    # slabs
    d.rect(0, 0, SLAB, TOP_T, "wood")
    # front slab layers, back to front
    y = SLAB + GAP
    for name, w, cls in (("main", MAIN, "wood"), ("backing", BACK, "face"), ("dog strip", STRIP, "leg"), ("laminate", LAM, "wood")):
        d.rect(y, 0, y + w, TOP_T, cls)
        y += w
    # square dog notch cut in the dog strip (open to the backing strip)
    fy1 = W - DOG_FRONT1
    d.rect(fy1, 0, fy1 + DOG, DOG, "hole")
    # ledges + bridge
    d.rect(SLAB, LEDGE_DROP, SLAB + LEDGE_W, LEDGE_DROP + LEDGE_H, "leg")
    d.rect(SLAB + GAP - LEDGE_W, LEDGE_DROP, SLAB + GAP, LEDGE_DROP + LEDGE_H, "leg")
    d.rect(SLAB + (GAP - BRIDGE_W) / 2, 0, SLAB + (GAP + BRIDGE_W) / 2, BRIDGE_T, "bridge")
    # tail-vise screw in its channel (est.)
    sy = W - SCREW_FROM_FRONT
    circle(d, sy, 2.2, 0.7, "metal")
    d.rect(sy - 0.9, 1.4, sy + 0.9, 3.0, "outl")
    # labels
    d.text(d.x(SLAB / 2), d.y(TOP_T / 2), f"rear slab {frac(SLAB)}", "n")
    d.text(d.x(SLAB + GAP + MAIN / 2), d.y(0.8), f"front slab, main {frac(MAIN)}", "n")
    d.leader(d.x(SLAB + GAP / 2), d.y(0) - 2, d.x(SLAB + GAP / 2 - 1.5), d.y(0) - 34, f"bridge {frac(BRIDGE_W)} × {frac(BRIDGE_T)}", "end", "red")
    d.leader(d.x(SLAB + LEDGE_W / 2), d.y(LEDGE_DROP + LEDGE_H), d.x(SLAB - 2.2), d.y(TOP_T) + 28, f"ledge {frac(LEDGE_W)} × {frac(LEDGE_H)}", "end")
    d.leader(d.x(sy), d.y(3.0), d.x(sy - 2.0), d.y(TOP_T) + 28, "tail-vise screw (est. 5½″ from front)", "end")
    d.leader(d.x(fy1 + DOG / 2), d.y(0.4), d.x(fy1 - 4.2), d.y(0) - 24, "¾″ square dog notch", "end")
    # dimensions
    yb = d.y(TOP_T) + 60
    d.dim_h(0, SLAB, yb, frac(SLAB), d.y(TOP_T))
    d.dim_h(SLAB, SLAB + GAP, yb, frac(GAP), d.y(TOP_T))
    d.dim_h(SLAB + GAP, SLAB + GAP + MAIN, yb, frac(MAIN), d.y(TOP_T))
    d.dim_h(SLAB + GAP + MAIN, SLAB + GAP + MAIN + BACK, yb, "", d.y(TOP_T))
    d.dim_h(W - LAM - STRIP, W - LAM, yb, "", d.y(TOP_T))
    d.dim_h(W - LAM, W, yb, frac(LAM), d.y(TOP_T))
    d.dim_h(0, W, yb + 28, frac(W), d.y(TOP_T))
    d.dim_v(0, TOP_T, d.x(-1.2), frac(TOP_T), d.x(0))
    d.text(d.x(W - LAM - STRIP / 2), yb - 4 + 28 * 0, "", "n")
    d.text(d.x(0), d.y(TOP_T) + 110, "rear", "n", "start")
    d.text(d.x(0), d.y(TOP_T) + 140, f"Front slab, back to front: main {frac(MAIN)}, backing {frac(BACK)}, dog strip {frac(STRIP)}, laminate {frac(LAM)} (est.). Notch is cut in the strip and closed by the backing.", "n", "start")
    d.text(d.x(W), d.y(TOP_T) + 110, "front", "n", "end")
    d.save(path, "Split-top Roubo bench, top cross-section with gap bridge and dog strip", EXTRA)


# ===========================================================================
# 5. Tail-vise layout, plan, tail end
# ===========================================================================
def tailvise(path):
    S = 16
    X0 = 56.0
    d = Drawing(1000, 640, 40, 100, s=S)
    px = lambda x: x - X0
    d.text(20, 26, "Tail-vise layout, plan of the tail end (1 in = 16 px)", "h", "start")
    sy = W - SCREW_FROM_FRONT
    # slabs
    d.rect(px(X0), 0, px(SLAB_L), SLAB, "wood")
    d.rect(px(X0), SLAB + GAP, px(SLAB_L), W, "wood")
    d.rect(px(X0), SLAB, px(SLAB_L), SLAB + GAP, "bridge")
    for yy in (W - LAM, W - LAM - STRIP, W - LAM - STRIP - BACK):
        d.line(px(X0), yy, px(SLAB_L), yy, "hid")
    for k in range(DOG_N):
        x0 = DOG_X0 + k * DOG_PITCH
        if x0 + DOG > X0:
            d.rect(px(x0), W - DOG_FRONT1, px(x0 + DOG), W - DOG_FRONT0, "hole")
    # end cap, closed
    d.rect(px(SLAB_L), 0, px(L), W, "cap")
    # screw, nut plate, guide rails, dog block
    d.add(f'<line class="scr" x1="{d.x(px(SLAB_L - SCREW_LEN)):.1f}" y1="{d.y(sy):.1f}" x2="{d.x(px(L + 1.2)):.1f}" y2="{d.y(sy):.1f}"/>')
    d.rect(px(SLAB_L - SCREW_LEN - 1.0), sy - 1.6, px(SLAB_L - SCREW_LEN + 1.0), sy + 1.6, "plate")
    d.rect(px(SLAB_L - SCREW_LEN + 1.0), sy - 1.0, px(SLAB_L), sy - 0.6, "metal")
    d.rect(px(SLAB_L - SCREW_LEN + 1.0), sy + 0.6, px(SLAB_L), sy + 1.0, "metal")
    d.rect(px(L + 1.2), sy - 3.2, px(L + 2.6), sy + 3.2, "metal")
    d.rect(px(SLAB_L - BLOCK_L), W - DOG_FRONT1, px(SLAB_L), W - DOG_FRONT0, "leg")
    # open position (ghost)
    d.rect(px(L + TRAVEL), 0, px(L + TRAVEL + CAP_T), W, "ghost")
    d.rect(px(SLAB_L + TRAVEL - BLOCK_L), W - DOG_FRONT1, px(SLAB_L + TRAVEL), W - DOG_FRONT0, "ghost")
    arrow(d, d.x(px(L + 0.3)), d.y(-5) + 0, d.x(px(L + TRAVEL)), d.y(-5) + 0)
    d.text(d.x(px(L + TRAVEL / 2)), d.y(-5) - 8, f"travel ~{TRAVEL:g}″ (verify)", "red")
    # labels
    d.leader(d.x(px(SLAB_L - SCREW_LEN)), d.y(sy) - 18, d.x(px(SLAB_L - SCREW_LEN)) - 10, d.y(sy) - 70, "sliding plate / nut", "end")
    d.leader(d.x(px(SLAB_L - 9)), d.y(sy) - 4, d.x(px(SLAB_L - 9)), d.y(sy) - 70, f"{SCREW_LEN:g}″ Acme screw", "middle")
    d.leader(d.x(px(SLAB_L - 2.5)), d.y(sy - 1.0), d.x(px(SLAB_L - 2.5)) - 10, d.y(sy) - 100, "guide rails", "end")
    d.leader(d.x(px(SLAB_L - BLOCK_L / 2)), d.y(W - DOG_FRONT0) + 2, d.x(px(SLAB_L - BLOCK_L / 2)) - 20, d.y(W) + 34, f"dog block, {frac(BLOCK_L)} long", "end")
    d.text(d.x(px(SLAB_L + CAP_T / 2)), d.y(7), "end cap", "n")
    d.text(d.x(px(SLAB_L + CAP_T / 2)), d.y(8.2), f"{frac(CAP_T)} × {frac(TOP_T)} × {frac(W)}", "n")
    d.text(d.x(px(SLAB_L + TRAVEL + CAP_T / 2)), d.y(W / 2), "open", "n")
    d.leader(d.x(px(L + 2)), d.y(sy) + 14, d.x(px(L + 2)) + 12, d.y(sy) + 52, "handwheel", "start")
    d.dim_h(px(SLAB_L - SCREW_LEN), px(SLAB_L), d.y(W) + 56, f"{SCREW_LEN:g}″ screw run", d.y(W)) if False else None
    d.dim_h(SLAB_L - X0, L - X0, d.y(0) - 24, frac(CAP_T), d.y(0))
    d.dim_v(sy, W, d.x(px(X0)) - 6, frac(SCREW_FROM_FRONT) + " (est.)", d.x(px(X0)))
    d.dim_h(SLAB_L - SCREW_LEN - X0, SLAB_L - X0, d.y(W) + 62, f"{SCREW_LEN:g}″ screw, so the cavity is {frac(SCREW_LEN - 1)}+ long", d.y(W))
    d.save(path, "Split-top Roubo bench, tail-vise layout in plan", EXTRA)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    front(os.path.join(OUT, "roubo-front.svg"))
    plan(os.path.join(OUT, "roubo-plan.svg"))
    end(os.path.join(OUT, "roubo-end.svg"))
    section(os.path.join(OUT, "roubo-top-section.svg"))
    tailvise(os.path.join(OUT, "roubo-tail-vise.svg"))
    print("legs", frac(LEG_LEN), "slab length", frac(SLAB_L), "gap", frac(GAP), "bridge", frac(BRIDGE_W))
    print("main", frac(MAIN), "dog notch from front", frac(DOG_FRONT0), "-", frac(DOG_FRONT1))
    print("last dog x", DOG_X0 + (DOG_N - 1) * DOG_PITCH)
