#!/usr/bin/env python3
"""True-scale SVGs for the Shaker 2-Drawer Coffee Table plan (fits an existing 19½″ × 48″ top).

Usage: python3 tools/woodworking/coffee_table_drawings.py
Writes public/static/woodworking/coffee-table-{front,side,plan,legs,drawer}.svg
All geometry is in inches; S is pixels per inch. Edit the constants, re-run.
Reuses the Drawing helper from modern_craftsman_drawings.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from modern_craftsman_drawings import Drawing, frac

S = 12
W, D, H = 48, 19.5, 18          # top (stated by user) and overall height (chosen)
TOP_T = 1.0                     # ASSUMED — measure the real top; legs = H - TOP_T
OVH_END, OVH_FB = 2.5, 1.0
FRAME_W, FRAME_D = W - 2 * OVH_END, D - 2 * OVH_FB      # 43 x 17.5
LEG = 2.0
APRON_T = 0.75
REVEAL, DIV = 1 / 16, 0.75
DR_W, DR_H = 19.0, 3.5
LOW_RAIL_H = 1.25
OPEN_H = REVEAL + DR_H + REVEAL                          # 3 5/8 drawer opening
APRON_H = OPEN_H + LOW_RAIL_H                            # 4 7/8
ARCH_RISE = 1.0
RAIL_T, RAIL_H = 1.25, 2.0                               # shelf side rails
RAIL_TOP = 6.5                                           # floor to rail top
SHELF_T, SHELF_TOP = 0.75, 6.0
SHELF_W = FRAME_W - 2 * RAIL_T                           # 40.5
SHELF_D = 12.75
BOX_W, BOX_D, BOX_H = 18.125, 14.0, 2.75                  # drawer box outside; BOX_D is behind the front
DR_T = 0.75                                              # drawer front thickness
BOX_SIDE_T, BOX_BOT_T = 0.5, 0.25                        # beech sides/back, bottom
DT_LAP = 0.25                                            # half-blind lap left on the front's face
GROOVE_UP, GROOVE_D = 0.25, 0.25                         # bottom groove: up from lower edge, depth
# Leg joinery, measured down from the top of the leg (see the plan's tenon table)
LEG_L = H - TOP_T
TEN_BACK = (0.25, 1.5)                                   # back apron
TEN_END = (1.75, 3.5)                                    # end apron
TEN_RAIL = (OPEN_H, OPEN_H + LOW_RAIL_H)                 # lower front rail (full height)
TEN_SHELF = (LEG_L - RAIL_TOP + 0.25, LEG_L - RAIL_TOP + RAIL_H - 0.25)   # shelf end rail, ¼″ shoulders
TEN_T, TEN_T_SHELF = 0.375, 0.5                          # tenon thicknesses (centred on the part)
TEN_LEN = 1.0
RUN_T, RUN_H, RUN_TOP = 0.75, 2.5, 0.75                  # runner thickness, height, top below top underside


def floor_line(d, x0, x1):
    d.add(f'<line class="floor" x1="{d.x(x0):.1f}" y1="{d.y(H):.1f}" x2="{d.x(x1):.1f}" y2="{d.y(H):.1f}"/>')


def front(path):
    d = Drawing(900, 440, 95, 100)
    leg_l, leg_r = OVH_END, OVH_END + FRAME_W - LEG
    open_l, open_r = leg_l + LEG, leg_r
    cx = (open_l + open_r) / 2
    d.text(20, 24, "Front elevation — 1 in = 12 px", "h", "start")
    d.rect(OVH_END + RAIL_T, H - SHELF_TOP, OVH_END + FRAME_W - RAIL_T, H - SHELF_TOP + SHELF_T, "shelf")
    d.rect(0, 0, W, TOP_T, "wood")
    d.rect(leg_l, TOP_T, leg_l + LEG, H, "leg")
    d.rect(leg_r, TOP_T, leg_r + LEG, H, "leg")
    r_top = TOP_T + OPEN_H
    d.rect(open_l, r_top, open_r, r_top + LOW_RAIL_H, "wood")
    d.rect(cx - DIV / 2, TOP_T, cx + DIV / 2, r_top, "wood")
    dt = TOP_T + REVEAL
    spans = ((open_l + REVEAL, cx - DIV / 2 - REVEAL), (cx + DIV / 2 + REVEAL, open_r - REVEAL))
    for a, b in spans:
        d.rect(a, dt, b, dt + DR_H, "face")
        m = (a + b) / 2
        d.add(f'<circle class="pull" cx="{d.x(m):.1f}" cy="{d.y(dt + DR_H/2):.1f}" r="{0.75*S:.1f}"/>')
        d.text(d.x(m), d.y(dt + 0.8), "19″ × 3½″", "n")
    floor_line(d, -3, W + 3)
    d.text(d.x(cx), d.y(9.2), "open below the rail", "n")
    d.text(d.x(cx), d.y(H - SHELF_TOP) - 6, "shelf (behind front legs)", "n")
    # dims
    d.dim_h(0, W, 42, "48″ top (existing)", pyo=d.y(0))
    d.dim_h(0, OVH_END, 68, "2½″", pyo=d.y(0))
    d.dim_h(OVH_END, OVH_END + FRAME_W, 68, "43″ leg frame", pyo=d.y(TOP_T))
    d.dim_h(OVH_END + FRAME_W, W, 68, "2½″", pyo=d.y(0))
    d.dim_v(0, H, 52, "18″ overall", pxo=d.x(0))
    d.dim_v(0, TOP_T, d.x(W) + 22, "", pxo=d.x(W), left=False)
    d.text(d.x(W) + 30, d.y(0.7), "1″ top (assumed)", "n", "start")
    d.dim_v(TOP_T, TOP_T + OPEN_H, d.x(W) + 22, f"{frac(OPEN_H)}", pxo=d.x(leg_r + LEG) + 3, left=False)
    d.dim_v_text(TOP_T + OPEN_H, TOP_T + OPEN_H + LOW_RAIL_H, d.x(W) + 22, f"{frac(LOW_RAIL_H)} rail",
                 pxo=d.x(leg_r + LEG) + 3)
    d.dim_v(H - SHELF_TOP, H, d.x(W) + 22, f"{frac(SHELF_TOP)} to shelf", pxo=d.x(W) - 3, left=False)
    d.dim_v(TOP_T + OPEN_H + LOW_RAIL_H, H, d.x(W) + 100, f"{frac(H - TOP_T - OPEN_H - LOW_RAIL_H)} to rail bottom",
            pxo=d.x(leg_r + LEG) + 3, left=False)
    yb = d.y(H) + 28
    d.dim_h(leg_l, leg_l + LEG, yb, "2″", pyo=d.y(H), below=True)
    d.dim_h(open_l, open_r, yb, "39″ opening", pyo=d.y(H), below=True)
    d.dim_h(leg_r, leg_r + LEG, yb, "2″", pyo=d.y(H), below=True)
    d.text(d.x(cx), yb + 40, "1/16″ reveals · ¾″ center divider · 1¼″ lower rail · 1½″ turned knobs", "n")
    d.save(path, "Shaker 2-drawer coffee table, front elevation")


def side(path):
    d = Drawing(660, 440, 95, 100)
    fl, fl2 = OVH_FB, OVH_FB + LEG
    bl, bl2 = D - OVH_FB - LEG, D - OVH_FB
    d.text(20, 24, "Side elevation — 1 in = 12 px", "h", "start")
    d.rect(0, 0, D, TOP_T, "wood")
    d.rect(fl, TOP_T, fl2, H, "leg")
    d.rect(bl, TOP_T, bl2, H, "leg")
    # arched end apron
    y0, y1 = TOP_T, TOP_T + APRON_H
    c = bl - fl2
    R = (c * c / 4 + ARCH_RISE ** 2) / (2 * ARCH_RISE)
    d.add(f'<path class="face" d="M{d.x(fl2):.1f},{d.y(y0):.1f} L{d.x(bl):.1f},{d.y(y0):.1f} '
          f'L{d.x(bl):.1f},{d.y(y1):.1f} A{R*S:.1f},{R*S:.1f} 0 0 0 {d.x(fl2):.1f},{d.y(y1):.1f} Z"/>')
    ry = H - RAIL_TOP
    d.rect(fl2, ry, bl, ry + RAIL_H, "face")
    d.text(d.x((fl2 + bl) / 2), d.y(ry + RAIL_H / 2) + 4, "shelf rail 1¼″ × 2″", "n")
    bt = TOP_T + REVEAL + (DR_H - BOX_H) / 2
    d.add(f'<rect class="hid" x="{d.x(fl+0.75):.1f}" y="{d.y(bt):.1f}" width="{BOX_D*S:.1f}" height="{BOX_H*S:.1f}"/>')
    floor_line(d, -3, D + 3)
    d.text(d.x(0.5), d.y(H) - 8, "front", "n", "start")
    d.dim_h(0, D, 42, "19½″ top", pyo=d.y(0))
    d.dim_h(0, OVH_FB, 68, "1″", pyo=d.y(0))
    d.dim_h(OVH_FB, D - OVH_FB, 68, "17½″ leg frame", pyo=d.y(TOP_T))
    d.dim_h(D - OVH_FB, D, 68, "1″", pyo=d.y(0))
    d.dim_v(0, H, 52, "18″ overall", pxo=d.x(0))
    d.dim_v(TOP_T, TOP_T + APRON_H, d.x(D) + 22, f"{frac(APRON_H)} apron", pxo=d.x(bl2), left=False)
    d.dim_v_text(ry, ry + RAIL_H, d.x(D) + 22, f"{frac(RAIL_H)} rail", pxo=d.x(bl2))
    d.dim_v(ry, H, d.x(D) + 96, f"{frac(RAIL_TOP)} to rail top", pxo=d.x(D) + 66, left=False)
    # arch rise, measured up from the chord between the shoulders
    d.line(fl2, y1, bl, y1, "ext")
    d.dim_v_text(y1 - ARCH_RISE, y1, d.x((fl2 + bl) / 2), f"{ARCH_RISE:g}″ rise")
    yb = d.y(H) + 28
    d.dim_h(fl, fl2, yb, "2″", pyo=d.y(H), below=True)
    d.dim_h(fl2, bl, yb, "13½″ between legs", pyo=d.y(H), below=True)
    d.dim_h(bl, bl2, yb, "2″", pyo=d.y(H), below=True)
    d.text(d.x(0), yb + 44, f"End apron ¾″ × 4⅞″ with a {ARCH_RISE:g}″-rise arch (R ≈ {R:.1f}″, est.).", "n", "start")
    d.text(d.x(0), yb + 60, "Dashed = drawer box, 14″ deep, hidden behind the apron.", "n", "start")
    d.save(path, "Shaker 2-drawer coffee table, side elevation")


def plan(path):
    oy = 100
    d = Drawing(900, 444, 95, oy)
    Y = lambda dep: d.oy + (D - dep) * S
    def prect(x1, dep1, x2, dep2, cls):
        d.add(f'<rect class="{cls}" x="{d.x(x1):.2f}" y="{Y(dep2):.2f}" width="{(x2-x1)*S:.2f}" height="{(dep2-dep1)*S:.2f}"/>')
    d.text(20, 24, "Plan view, top removed — 1 in = 12 px", "h", "start")
    leg_l, leg_r = OVH_END, OVH_END + FRAME_W - LEG
    fl, fl2 = OVH_FB, OVH_FB + LEG
    bl, bl2 = D - OVH_FB - LEG, D - OVH_FB
    cx = W / 2
    d.add(f'<rect class="hid" x="{d.x(0):.1f}" y="{Y(D):.1f}" width="{W*S}" height="{D*S}"/>')
    # shelf rails (below), shelf
    for x in (leg_l, W - OVH_END - RAIL_T):
        prect(x, fl2, x + RAIL_T, bl, "face")
    sd0 = fl2 + (bl - fl2 - SHELF_D) / 2
    prect(OVH_END + RAIL_T, sd0, W - OVH_END - RAIL_T, sd0 + SHELF_D, "shelf")
    # end aprons + slide spacers
    for x in (leg_l, W - OVH_END - APRON_T):
        prect(x, fl2, x + APRON_T, bl, "wood")
    prect(leg_l + APRON_T, fl2, leg_l + LEG, bl, "spacer")
    prect(leg_r, fl2, leg_r + LEG - APRON_T, bl, "spacer")
    # back apron, lower front rail
    prect(leg_l + LEG, bl2 - APRON_T, leg_r, bl2, "wood")
    prect(leg_l + LEG, fl, leg_r, fl + APRON_T, "wood")
    # runner + divider
    prect(cx - RUN_T / 2, fl + APRON_T, cx + RUN_T / 2, bl2 - APRON_T, "wood")
    prect(cx - DIV / 2, fl, cx + DIV / 2, fl + APRON_T, "wood")
    for x in (leg_l, leg_r):
        prect(x, fl, x + LEG, fl2, "leg")
        prect(x, bl, x + LEG, bl2, "leg")
    # drawers
    for c in (cx - DIV / 2 - REVEAL - DR_W / 2, cx + DIV / 2 + REVEAL + DR_W / 2):
        prect(c - DR_W / 2, fl, c + DR_W / 2, fl + APRON_T, "face")
        d.add(f'<rect class="hid" x="{d.x(c-BOX_W/2):.1f}" y="{Y(fl+APRON_T+BOX_D):.1f}" width="{BOX_W*S:.1f}" height="{BOX_D*S:.1f}"/>')
        d.text(d.x(c), Y(fl + 8.8), "drawer box 18⅛″ × 14″", "n")
        d.text(d.x(c), Y(fl + 7.6), "(dashed; on 14″ slides)", "n")
    d.text(d.x(cx + 1), Y(16.8), "◀ runner ¾″", "n", "start")
    d.text(d.x(cx), Y(0) + 14, "FRONT", "n")
    # mounting openings (leg/spacer face to runner) along the front
    mo = (FRAME_W - 2 * LEG - RUN_T) / 2
    yb = Y(0) + 36
    d.dim_h(leg_l + LEG, cx - RUN_T / 2, yb, f"{frac(mo)} mounting opening", pyo=Y(fl), below=True)
    d.dim_h(cx + RUN_T / 2, leg_r, yb, f"{frac(mo)} mounting opening", pyo=Y(fl), below=True)
    # free depth behind the right-hand box
    fx = d.x(cx + RUN_T / 2 + mo - 3)
    d.dim_v_text(D - (bl2 - APRON_T), D - (fl + APRON_T + BOX_D), fx, f"{frac(bl2 - APRON_T - fl - APRON_T - BOX_D)} free",
                 side="left")
    d.text(d.x(0), Y(0) + 70, "Dashed outline = existing top, 48″ × 19½″, floating on buttons.  Dark tan = legs.  Grey = 1¼″ × 3″ slide spacers.", "n", "start")
    d.text(d.x(0), Y(0) + 86, "Light tan under the drawers = shelf, 40½″ × 12¾″ × ¾″.  Boxes sit ½″ off each mounting face on side-mount slides;", "n", "start")
    d.text(d.x(0), Y(0) + 102, "≈ 2″ of free depth is left behind each box before the back apron.", "n", "start")
    d.dim_h(0, W, 42, "48″ top", pyo=Y(D))
    d.dim_h(0, OVH_END, 68, "2½″", pyo=Y(D))
    d.dim_h(OVH_END, OVH_END + FRAME_W, 68, "43″ leg frame", pyo=Y(bl2))
    d.dim_h(OVH_END + FRAME_W, W, 68, "2½″", pyo=Y(D))
    def dim_depth(dep1, dep2, px, label):
        a, b = Y(dep1), Y(dep2)
        d.add(f'<line class="dim" x1="{px}" y1="{a:.1f}" x2="{px}" y2="{b:.1f}" marker-start="url(#a)" marker-end="url(#a)"/>')
        d.add(f'<text class="t" transform="translate({px+14},{(a+b)/2:.1f}) rotate(-90)" text-anchor="middle">{label}</text>')
    dim_depth(0, D, d.x(W) + 24, "19½″ top")
    dim_depth(fl, bl2, d.x(W) + 54, "17½″ leg frame")
    d.dim_v(D - bl, D - fl2, d.x(0) - 24, f"{frac(bl - fl2)} between legs", pxo=d.x(leg_l), left=False)
    d.save(path, "Shaker 2-drawer coffee table, plan view")


EXTRA = """<style>
  .mort{fill:#6b4a2f;stroke:#2b1a0f;stroke-width:1}
  .box{fill:#f1e4c8;stroke:#4a3320;stroke-width:1.2}
  .bot{fill:#faf3e3;stroke:#4a3320;stroke-width:1}
  .dt{fill:url(#hatch);stroke:#4a3320;stroke-width:1}
  .hid2{fill:none;stroke:#b0452b;stroke-width:1.1;stroke-dasharray:2 3}
  .far{fill:#faf3e3;stroke:#8a7560;stroke-width:1}
</style>
<defs>
  <pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <rect width="5" height="5" fill="#f1e4c8"/><line x1="0" y1="0" x2="0" y2="5" stroke="#4a3320" stroke-width="1"/>
  </pattern>
</defs>
"""


def legs(path):
    """Mortise layout on the two left-hand legs (the right-hand pair is a mirror image).
    Left block: the mortised faces, true length. Right block: the leg tops, larger, with
    every mortise dashed so the gauge offsets and depths read directly."""
    d = Drawing(900, 680, 0, 0)
    d.text(20, 24, "Leg mortise layout — faces at 1 in = 18 px, leg tops at 1 in = 64 px", "h", "start")
    d.text(20, 44, f"Left-hand legs shown; the right-hand pair is a mirror image. Heights are measured down from "
           f"the top of the {frac(LEG_L)} leg.", "n", "start")
    s_face = 18
    apron_u = ((APRON_T - TEN_T) / 2, (APRON_T + TEN_T) / 2)          # 3/16 – 9/16 from the flush face
    shelf_u = ((RAIL_T - TEN_T_SHELF) / 2, (RAIL_T + TEN_T_SHELF) / 2)  # 3/8 – 7/8 from the outside face
    rng = lambda a, b: f"{frac(a)}–{frac(b)}"
    # (title, sub, edge labels left/right, mortises (top, bottom, u0, u1, name)); u runs across
    # the face as seen from outside it, 0 at its left edge
    faces = [
        ("FRONT leg", "inside face", ("front", "back"),
         [(*TEN_RAIL, apron_u[0], apron_u[1], "lower rail")]),
        ("FRONT leg", "back face", ("inside", "outside"),
         [(*TEN_END, LEG - apron_u[1], LEG - apron_u[0], "end apron"),
          (*TEN_SHELF, LEG - shelf_u[1], LEG - shelf_u[0], "shelf rail")]),
        ("BACK leg", "inside face", ("front", "back"),
         [(*TEN_BACK, LEG - apron_u[1], LEG - apron_u[0], "back apron")]),
        ("BACK leg", "front face", ("outside", "inside"),
         [(*TEN_END, apron_u[0], apron_u[1], "end apron"),
          (*TEN_SHELF, shelf_u[0], shelf_u[1], "shelf rail")]),
    ]
    top = 112
    for i, (title, sub, edges, morts) in enumerate(faces):
        d.s, d.oy = s_face, top
        d.ox = 150 + i * 110 + (30 if i >= 2 else 0)
        d.text(d.x(LEG / 2), top - 32, title, "t")
        d.text(d.x(LEG / 2), top - 16, sub, "n")
        d.rect(0, 0, LEG, LEG_L, "leg")
        for t0, t1, u0, u1, name in morts:
            d.rect(u0, t0, u1, t1, "mort")
            d.dim_v_text(t0, t1, d.x(0) - 8, rng(t0, t1), pxo=d.x(0), side="left")
            d.text(d.x(0) - 13, d.y(t1) + 12, name, "n", "end")
        d.text(d.x(0) - 2, d.y(LEG_L) + 14, edges[0], "n", "end")
        d.text(d.x(LEG) + 2, d.y(LEG_L) + 14, edges[1], "n", "start")
    d.ox, d.oy, d.s = 150, top, s_face
    d.dim_v(0, LEG_L, 40, f"{frac(LEG_L)} leg", pxo=d.x(0) - 4)
    sep = 150 + 2 * 110 - 17
    d.add(f'<line class="ext" x1="{sep}" y1="{top - 44}" x2="{sep}" y2="{top + LEG_L*s_face + 24}"/>')

    # ---- leg tops: plan, front of the table at the bottom, outside face at the left ----
    sp = 64
    def plan_leg(oy, title, morts, names):
        d.s, d.ox, d.oy = sp, 610, oy
        d.text(d.x(LEG / 2), oy - 62, title, "t")
        d.rect(0, 0, LEG, LEG, "leg")
        for (x1, y1, x2, y2, cls) in morts:
            d.rect(x1, y1, x2, y2, cls)
        # face names inside the square, clear of the mortises
        for (u, v, label, rot) in names:
            if rot:
                d.add(f'<text class="n" transform="translate({d.x(u):.1f},{d.y(v):.1f}) rotate(-90)" '
                      f'text-anchor="middle">{label}</text>')
            else:
                d.text(d.x(u), d.y(v), label, "n")

    # FRONT leg: end apron + shelf rail enter the back face (top edge); lower rail the inside face (right)
    oyf = 150
    plan_leg(oyf, "FRONT leg, top view", [
        (LEG - TEN_LEN, LEG - apron_u[1], LEG, LEG - apron_u[0], "hid"),       # lower rail
        (apron_u[0], 0, apron_u[1], TEN_LEN, "hid"),                           # end apron
        (shelf_u[0], 0, shelf_u[1], TEN_LEN, "hid2")],                         # shelf rail
        [(LEG * 0.72, 0.28, "back", False), (LEG * 0.28, LEG - 0.1, "front", False),
         (0.15, LEG * 0.75, "outside", True), (LEG - 0.08, LEG * 0.3, "inside", True)])
    d.dim_h(*apron_u, oyf - 12, rng(*apron_u), pyo=d.y(0))
    d.dim_h(*shelf_u, oyf - 38, rng(*shelf_u), pyo=d.y(0))
    d.dim_v_text(0, TEN_LEN, d.x(0) - 12, frac(TEN_LEN), pxo=d.x(apron_u[0]), side="left")
    d.dim_v_text(LEG - apron_u[1], LEG - apron_u[0], d.x(LEG) + 12, f"{rng(*apron_u)} from front", pxo=d.x(LEG))
    d.dim_h(LEG - TEN_LEN, LEG, d.y(LEG) + 24, frac(TEN_LEN), pyo=d.y(LEG - apron_u[0]), below=True)

    # BACK leg: back apron enters the inside face near the back; end apron + shelf rail the front face
    oyb = 400
    plan_leg(oyb, "BACK leg, top view", [
        (LEG - TEN_LEN, apron_u[0], LEG, apron_u[1], "hid"),                   # back apron
        (apron_u[0], LEG - TEN_LEN, apron_u[1], LEG, "hid"),                   # end apron
        (shelf_u[0], LEG - TEN_LEN, shelf_u[1], LEG, "hid2")],                 # shelf rail
        [(LEG * 0.28, 0.28, "back", False), (LEG * 0.72, LEG - 0.1, "front", False),
         (0.15, LEG * 0.28, "outside", True), (LEG - 0.08, LEG * 0.7, "inside", True)])
    d.dim_h(LEG - TEN_LEN, LEG, oyb - 12, frac(TEN_LEN), pyo=d.y(apron_u[0]))
    d.dim_v_text(*apron_u, d.x(LEG) + 12, f"{rng(*apron_u)} from back", pxo=d.x(LEG))
    d.dim_v_text(LEG - TEN_LEN, LEG, d.x(0) - 12, frac(TEN_LEN), pxo=d.x(apron_u[0]), side="left")
    d.dim_h(*apron_u, d.y(LEG) + 22, rng(*apron_u), pyo=d.y(LEG), below=True)
    d.dim_h(*shelf_u, d.y(LEG) + 48, rng(*shelf_u), pyo=d.y(LEG), below=True)

    # notes
    d.ox, d.oy, d.s = 0, 0, S
    ny = 626
    d.text(20, ny, f"Dashed grey = {frac(TEN_T)} mortises for the ¾″ parts (end and back aprons, lower rail), "
           f"{frac(apron_u[0])} in from the face the part is flush with.", "n", "start")
    d.text(20, ny + 16, f"Dotted red = {frac(TEN_T_SHELF)} mortises for the 1¼″ shelf end rails, {frac(shelf_u[0])} in "
           "from the outside face. Tenons are centred on each part's thickness.", "n", "start")
    d.text(20, ny + 32, f"All tenons are {frac(TEN_LEN)} long, so cut the mortises a little deeper. Every part is flush "
           "with an outside face, so mortises on adjacent faces never meet.", "n", "start")
    d.save(path, "Shaker 2-drawer coffee table, leg mortise layout", extra=EXTRA)


def drawer(path):
    """Drawer box: plan section above the bottom, and a side section on the centre line."""
    d = Drawing(820, 744, 110, 124, s=20)
    d.text(20, 24, "Drawer box — plan section at 1 in = 20 px, side section at 1 in = 24 px", "h", "start")
    d.text(20, 44, "Two identical drawers. Beech box, half-blind dovetails into the cherry front, "
           "through dovetails at the back. Hatched = dovetailed corners.", "n", "start")
    depth = DR_T + BOX_D                       # front face of the drawer front → back face of the box
    xl = (DR_W - BOX_W) / 2                    # 7/16 overhang
    xr = xl + BOX_W
    sd0 = DR_T - (DR_T - DT_LAP)               # side starts behind the ¼″ lap
    side_len = depth - sd0
    bw = BOX_W - 2 * BOX_SIDE_T + 2 * GROOVE_D
    bd = depth - (DR_T - GROOVE_D)
    Y = lambda dep: depth - dep                # front at the bottom of the plan
    def prect(x1, a, x2, b, cls):
        d.rect(x1, Y(b), x2, Y(a), cls)
    d.text(20, 76, "Plan section (front at the bottom)", "t", "start")
    prect(xl + BOX_SIDE_T - GROOVE_D, DR_T - GROOVE_D, xr - BOX_SIDE_T + GROOVE_D, depth, "bot")
    prect(0, 0, DR_W, DR_T, "face")
    for x0 in (xl, xr - BOX_SIDE_T):
        prect(x0, sd0, x0 + BOX_SIDE_T, depth, "box")
        prect(x0, sd0, x0 + BOX_SIDE_T, DR_T, "dt")
        prect(x0, depth - BOX_SIDE_T, x0 + BOX_SIDE_T, depth, "dt")
    prect(xl + BOX_SIDE_T, depth - BOX_SIDE_T, xr - BOX_SIDE_T, depth, "box")
    prect(xl + BOX_SIDE_T - GROOVE_D, DR_T - GROOVE_D, xr - BOX_SIDE_T + GROOVE_D, depth, "hid")
    d.text(d.x(DR_W / 2), d.y(Y(depth / 2)) - 8, f"bottom {frac(BOX_BOT_T)}, ≈ {frac(bw)} × {frac(bd)}", "n")
    d.text(d.x(DR_W / 2), d.y(Y(depth / 2)) + 8, "(dashed = its edges, in the grooves and under the back)", "n")
    d.add(f'<text class="n" transform="translate({d.x(xl + BOX_SIDE_T) + 20:.1f},{d.y(Y(depth/2)):.1f}) rotate(-90)" '
          f'text-anchor="middle">side {frac(BOX_SIDE_T)} × {frac(BOX_H)} × {frac(side_len)}</text>')
    # inside width
    d.dim_h(xl + BOX_SIDE_T, xr - BOX_SIDE_T, d.y(Y(depth * 0.3)), f"{frac(BOX_W - 2 * BOX_SIDE_T)} inside")
    # dims: back length on top, box + front below
    d.dim_h(xl, xr, d.y(0) - 14, f"back {frac(BOX_SIDE_T)} × {frac(BOX_H - GROOVE_UP - GROOVE_D)} × {frac(BOX_W)} (full box width)", pyo=d.y(0))
    yb = d.y(depth) + 24
    d.dim_h_small(0, xl, yb, frac(xl), pyo=d.y(depth), side="left")
    d.dim_h(xl, xr, yb, f"{frac(BOX_W)} box", pyo=d.y(Y(sd0)), below=True)
    d.dim_h(0, DR_W, yb + 30, f"{frac(DR_W)} front", pyo=d.y(depth), below=True)
    px = d.x(DR_W) + 16
    d.dim_v_text(Y(DR_T), Y(0), px, f"{frac(DR_T)} cherry front", pxo=d.x(DR_W))
    d.dim_v(Y(depth), Y(DR_T), px, f"{frac(BOX_D)} behind the front", pxo=d.x(xr), left=False)
    d.dim_v_text(Y(sd0), Y(0), d.x(0) - 14, f"{frac(DT_LAP)} lap", pxo=d.x(xl), side="left")

    # ---- side section on the centre line (front at the left, top up) ----
    s2 = 24
    d.s, d.ox, d.oy = s2, 110, 548
    d.text(20, d.oy - 40, "Side section on the centre line (front at the left)", "t", "start")
    bt = (DR_H - BOX_H) / 2                    # box top below the front's top edge (⅜)
    bb = bt + BOX_H
    g1 = bb - GROOVE_UP                        # groove lower edge
    g0 = g1 - GROOVE_D                         # groove upper edge = top of the bottom
    d.rect(sd0, bt, depth, bb, "far")           # the far side, seen beyond the cut
    d.rect(0, 0, DR_T, DR_H, "face")
    d.line(sd0, bt, sd0, bb, "hid")             # side's end inside the half-blind socket
    d.rect(depth - BOX_SIDE_T, bt, depth, g0, "box")    # back, cut
    d.rect(DR_T - GROOVE_D, g0, depth, g0 + BOX_BOT_T, "box")   # bottom, cut
    d.text(d.x((DR_T + depth) / 2), d.y((bt + g0) / 2) + 4, "inside face of the far side", "n")
    # dims
    d.dim_v(0, DR_H, d.x(0) - 52, f"{frac(DR_H)} front", pxo=d.x(0))
    d.dim_v_text(0, bt, d.x(0) - 12, frac(bt), pxo=d.x(0), side="left")
    d.dim_v_text(bb, DR_H, d.x(0) - 12, frac(DR_H - bb), pxo=d.x(0), side="left")
    pr = d.x(depth) + 14
    d.dim_v_text(bt, g0, pr, f"{frac(g0 - bt)} back", pxo=d.x(depth))
    d.dim_v_text(g0, g1, pr, "", pxo=d.x(depth))
    d.dim_v_text(g1, bb, pr, "", pxo=d.x(depth))
    d.text(pr + 5, d.y(g0) + 1, f"{frac(BOX_BOT_T)} bottom in a {frac(GROOVE_D)} × {frac(GROOVE_D)} groove", "t", "start")
    d.text(pr + 5, d.y(bb) + 13, f"groove {frac(GROOVE_UP)} up from the lower edge", "t", "start")
    d.dim_v(bt, bb, d.x(depth - 1.5), f"{frac(BOX_H)} box", left=True)
    yb = d.y(DR_H) + 24
    d.dim_h_small(0, DR_T, yb, frac(DR_T), pyo=d.y(DR_H), side="left")
    d.dim_h(DR_T, depth, yb, f"{frac(BOX_D)} behind the front", pyo=d.y(bb), below=True)
    d.dim_h(DR_T - GROOVE_D, depth, yb + 30, f"bottom ≈ {frac(bd)}, {frac(GROOVE_D)} into the front", pyo=d.y(g1), below=True)
    d.text(20, 720, f"Sides start {frac(DT_LAP)} behind the drawer face (half-blind sockets {frac(DR_T - DT_LAP)} deep). "
           f"Box is centred on the front, {frac(bt)} in from top and bottom; slides mount on the box sides.", "n", "start")
    d.save(path, "Shaker 2-drawer coffee table, drawer box detail", extra=EXTRA)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "..", "public", "static", "woodworking")
    os.makedirs(out, exist_ok=True)
    front(os.path.join(out, "coffee-table-front.svg"))
    side(os.path.join(out, "coffee-table-side.svg"))
    plan(os.path.join(out, "coffee-table-plan.svg"))
    legs(os.path.join(out, "coffee-table-legs.svg"))
    drawer(os.path.join(out, "coffee-table-drawer.svg"))
    print("wrote 5 SVGs to", os.path.normpath(out))
