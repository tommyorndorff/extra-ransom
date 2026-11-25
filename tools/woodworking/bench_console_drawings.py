#!/usr/bin/env python3
"""True-scale SVGs for the Cherry Console + Slide-Under Chest Bench plan.

Usage: python3 tools/woodworking/bench_console_drawings.py
Writes public/static/woodworking/bench-console-{front,side,plan,bench,chest-front}.svg
Geometry in inches. Edit the constants and re-run; every label is built from
them with frac(), so the drawings follow the numbers.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from modern_craftsman_drawings import Drawing, frac

S = 12                                              # px per inch (console views)
K = 16                                              # px per inch (chest views)

# console
W, D, H = 42, 15, 35
OV = 1.0
TOP_T, LEG = 0.75, 1.5
AP_T, AP_H = 0.75, 3.5                              # aprons
RAIL_T, RAIL_H, RAIL_TOP = 0.75, 2.5, 9.25          # lower rails; top edge off the floor
FR_W, FR_D = W - 2 * OV, D - 2 * OV                 # 40 x 13
L0, L1 = OV, OV + LEG                               # 1..2.5
R0, R1 = W - OV - LEG, W - OV                       # 39.5..41
F0, F1 = OV, OV + LEG                               # 1..2.5   (front legs, depth)
B0, B1 = D - OV - LEG, D - OV                       # 12.5..14 (back legs, depth)
APRON_BOT = TOP_T + AP_H                            # 4.25 from top surface -> 30.75 above floor

# chest bench
BW, BD, BH = 36.0, 13.0, 17.0
LID_T, PLINTH_H, INSET = 1.0, 2.25, 0.375
WALL, PL_T = 0.75, 0.75                             # case walls, plinth stock
CASE_H = BH - LID_T - PLINTH_H                      # 13.75
GROOVE_D, GROOVE_UP, BOT_T = 0.25, 0.25, 0.5        # bottom groove depth, its offset from the case edge, bottom thickness
BOT_W = BD - 2 * WALL + 2 * GROOVE_D - 0.125        # 11 7/8 (1/8 for movement)
BOT_L = BW - 2 * WALL + 2 * GROOVE_D                # 35
CLEAT_T, CLEAT_W, CLEAT_IN = 0.75, 1.25, 2.0
CLEAT_L = BD - 2 * WALL - 0.25                      # 11 1/4
IN_W, IN_D = BW - 2 * WALL, BD - 2 * WALL           # 34 1/2 x 11 1/2
IN_H = CASE_H - GROOVE_UP - BOT_T                   # 13 (lid underside to bottom)

# how the two fit
BACK_STOP = D - OV - RAIL_T                         # inner face of back rail: 13.25
BX0 = (W - BW) / 2                                  # 3.0
B_FRONT, B_BACK = BACK_STOP - BD, BACK_STOP         # 0.25..13.25 (depth)
LID_Y0 = H - BH                                     # lid top, from top surface = 18
CASE_Y0, PLINTH_Y0 = LID_Y0 + LID_T, LID_Y0 + LID_T + CASE_H
CLEAR = H - APRON_BOT                               # 30 3/4 under the apron
SPARE = CLEAR - (BH + BD)                           # 3/4 above the open lid (worst case)

EXTRA = """
<style>
  .beyond{fill:#f6efe4;stroke:#9a8a7a;stroke-width:1}
  .groove{fill:#fff;stroke:#4a3320;stroke-width:1}
  .dt{fill:url(#hatch);stroke:#4a3320;stroke-width:1.3}
  .knuckle{fill:#5a3b26;stroke:#2b1a0f;stroke-width:1}
</style>
<defs>
  <pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <rect width="6" height="6" fill="#e6c79c"/><line x1="0" y1="0" x2="0" y2="6" stroke="#4a3320" stroke-width="1"/>
  </pattern>
</defs>
"""


class D2(Drawing):
    """Local extras: extension lines whose two ends sit on different features."""

    def ext_h(self, y, x_from, px):
        """Horizontal extension line at height y (in) from feature x_from (in) to pixel column px."""
        self.add(f'<line class="ext" x1="{self.x(x_from):.1f}" y1="{self.y(y):.1f}" '
                 f'x2="{px:.1f}" y2="{self.y(y):.1f}"/>')

    def ext_v(self, x, y_from, py):
        """Vertical extension line at x (in) from feature y_from (in) to pixel row py."""
        self.add(f'<line class="ext" x1="{self.x(x):.1f}" y1="{self.y(y_from):.1f}" '
                 f'x2="{self.x(x):.1f}" y2="{py:.1f}"/>')


def _floor(d, a, b, y=H):
    d.add(f'<line class="floor" x1="{d.x(a):.1f}" y1="{d.y(y):.1f}" x2="{d.x(b):.1f}" y2="{d.y(y):.1f}"/>')


def front(path):
    d = D2(720, 620, 95, 100, s=S)
    d.text(20, 24, f"Front elevation, bench pushed in — 1 in = {S} px", "h", "start")
    d.rect(0, 0, W, TOP_T, "wood")
    d.rect(L0, TOP_T, L1, H, "leg"); d.rect(R0, TOP_T, R1, H, "leg")
    d.rect(L1, TOP_T, R0, APRON_BOT, "face")
    # bench
    d.rect(BX0 + INSET, PLINTH_Y0, BX0 + BW - INSET, H, "wood")
    d.rect(BX0, CASE_Y0, BX0 + BW, PLINTH_Y0, "shelf")
    d.rect(BX0, LID_Y0, BX0 + BW, CASE_Y0, "face")
    d.text(d.x(W / 2), d.y(CASE_Y0 + 6.5), "blanket chest bench", "n")
    d.text(d.x(W / 2), d.y(CASE_Y0 + 8.2), f"{frac(BW)} × {frac(BD)} × {frac(BH)}", "n")
    d.text(d.x(W / 2), d.y(TOP_T + AP_H / 2) + 4, f"front apron {frac(AP_T)} × {frac(AP_H)}", "n")
    d.text(d.x(W / 2), d.y(10), "open space above the lid", "n")
    _floor(d, -1, W + 1)
    # top rows
    d.dim_h(0, W, 42, f"{frac(W)} overall", pyo=d.y(0))
    d.dim_h(0, OV, 68, frac(OV), pyo=d.y(0))
    d.dim_h(OV, W - OV, 68, f"{frac(FR_W)} leg frame", pyo=d.y(TOP_T))
    d.dim_h(W - OV, W, 68, frac(OV), pyo=d.y(0))
    # left
    d.dim_v(0, H, 52, f"{frac(H)} overall", pxo=d.x(0))
    # right: chain floor -> lid -> apron -> top on col 1, clear height on col 2
    p1 = d.x(W) + 24
    p2 = p1 + 26
    d.ext_h(H, R1, p2)                       # floor
    d.ext_h(LID_Y0, BX0 + BW, p1)            # lid top
    d.ext_h(APRON_BOT, R0, p2)               # apron bottom edge
    d.ext_h(TOP_T, W, p1)                    # top underside
    d.ext_h(0, W, p1)                        # top surface
    d.dim_v(LID_Y0, H, p1, f"{frac(BH)} seat height", left=False)
    d.dim_v(APRON_BOT, LID_Y0, p1, f"{frac(LID_Y0 - APRON_BOT)} above lid", left=False)
    d.dim_v(TOP_T, APRON_BOT, p1, frac(AP_H), left=False)
    d.dim_v_text(0, TOP_T, p1, f"{frac(TOP_T)} top")
    d.dim_v(APRON_BOT, H, p2, f"{frac(CLEAR)} clear under apron", left=False)
    # bottom rows
    yb = d.y(H) + 28
    d.dim_h(L0, L1, yb, frac(LEG), pyo=d.y(H), below=True)
    d.dim_h(L1, R0, yb, f"{frac(R0 - L1)} between legs", pyo=d.y(H), below=True)
    d.dim_h(R0, R1, yb, frac(LEG), pyo=d.y(H), below=True)
    d.dim_h(BX0, BX0 + BW, yb + 28, f"{frac(BW)} bench — {frac(BX0 - L1)} clear each side",
            pyo=d.y(PLINTH_Y0), below=True)
    d.save(path, "Console with bench, front elevation", EXTRA)


def side(path):
    d = D2(560, 690, 95, 100, s=S)
    d.text(20, 24, f"Side elevation, lid open to vertical — 1 in = {S} px", "h", "start")
    ry = H - RAIL_TOP
    # bench first: the near legs, apron and side rail are in front of it
    d.rect(B_FRONT + INSET, PLINTH_Y0, B_BACK - INSET, H, "wood")
    d.rect(B_FRONT, CASE_Y0, B_BACK, PLINTH_Y0, "shelf")
    d.rect(B_FRONT, LID_Y0, B_BACK, CASE_Y0, "face")
    d.rect(0, 0, D, TOP_T, "wood")
    d.rect(F0, TOP_T, F1, H, "leg"); d.rect(B0, TOP_T, B1, H, "leg")
    d.rect(F1, TOP_T, B0, APRON_BOT, "face")
    d.rect(F1, ry, B0, ry + RAIL_H, "wood")               # side lower rail
    # back lower rail / stop: behind the near back leg (hidden)
    d.add(f'<rect class="hid" x="{d.x(B_BACK):.1f}" y="{d.y(ry):.1f}" width="{RAIL_T*S:.1f}" height="{RAIL_H*S:.1f}"/>')
    # lid open to vertical, drawn about the lid's top back edge (worst case)
    hx = B_BACK
    d.add(f'<rect class="hid" x="{d.x(hx-LID_T):.1f}" y="{d.y(LID_Y0-BD):.1f}" width="{LID_T*S:.1f}" height="{BD*S:.1f}"/>')
    x1, y1 = d.x(B_FRONT), d.y(LID_Y0)
    x2, y2 = d.x(hx), d.y(LID_Y0 - BD)
    d.add(f'<path class="hid" d="M{x1:.1f},{y1:.1f} A{BD*S:.1f},{BD*S:.1f} 0 0 1 {x2:.1f},{y2:.1f}"/>')
    d.text(d.x(7.6), d.y(LID_Y0 - 6.0), "lid front edge", "n")
    d.text(d.x(7.6), d.y(LID_Y0 - 6.0) + 14, "path (hinge at back)", "n")
    d.text(d.x((F1 + B0) / 2), d.y(TOP_T + AP_H / 2) + 4, "side apron", "n")
    d.text(d.x((F1 + B0) / 2), d.y(ry + RAIL_H / 2) + 4, "side rail", "n")
    d.text(d.x((F1 + B0) / 2), d.y(CASE_Y0 + 3.5), "chest (beyond", "n")
    d.text(d.x((F1 + B0) / 2), d.y(CASE_Y0 + 3.5) + 14, "the side rail)", "n")
    _floor(d, -1, D + 1)
    # top rows
    d.dim_h(0, D, 42, f"{frac(D)} overall", pyo=d.y(0))
    d.dim_h(0, OV, 68, frac(OV), pyo=d.y(0))
    d.dim_h(OV, D - OV, 68, f"{frac(FR_D)} leg frame", pyo=d.y(TOP_T))
    d.dim_h(D - OV, D, 68, frac(OV), pyo=d.y(0))
    d.dim_v(0, H, 52, f"{frac(H)} overall", pxo=d.x(0))
    # right: rail height, rail top off floor, then floor -> seat -> open lid -> apron
    p1 = d.x(D) + 24
    p2, p3 = p1 + 26, p1 + 52
    d.ext_h(ry + RAIL_H, B0, p2)            # rail bottom
    d.ext_h(ry, B0, p2)                     # rail top
    d.ext_h(H, B1, p3)                      # floor
    d.ext_h(LID_Y0, B_BACK, p3)             # lid top (closed)
    d.ext_h(LID_Y0 - BD, B_BACK, p3)        # open lid top
    d.ext_h(APRON_BOT, B0, p3)              # apron bottom
    d.dim_v(ry, ry + RAIL_H, p1, frac(RAIL_H), left=False)
    d.dim_v(ry, H, p2, f"{frac(RAIL_TOP)} rail top", left=False)
    d.dim_v(LID_Y0, H, p3, f"{frac(BH)} seat height", left=False)
    d.dim_v(LID_Y0 - BD, LID_Y0, p3, f"{frac(BD)} lid", left=False)
    d.dim_v_text(APRON_BOT, LID_Y0 - BD, p3, f"{frac(SPARE)} to spare")
    # bottom rows
    yb = d.y(H) + 28
    d.dim_h(F0, F1, yb, frac(LEG), pyo=d.y(H), below=True)
    d.dim_h(F1, B0, yb, f"{frac(B0 - F1)} between legs", pyo=d.y(H), below=True)
    d.dim_h(B0, B1, yb, frac(LEG), pyo=d.y(H), below=True)
    d.dim_h(B_FRONT, B_BACK, yb + 28, f"{frac(BD)} bench depth", pyo=d.y(PLINTH_Y0), below=True)
    yc = yb + 72
    d.text(20, yc, f"Front at left. Bench front sits {frac(B_FRONT)} behind the top's front edge.", "n", "start")
    d.text(20, yc + 16, "Arc drawn about the lid's top back edge (worst case); a piano hinge", "n", "start")
    d.text(20, yc + 32, "at the lid/case seam tops out about 1″ lower.", "n", "start")
    d.save(path, "Console with bench, side elevation with lid open", EXTRA)


def plan(path):
    oy = 100
    d = D2(700, 470, 95, oy, s=S)
    Y = lambda dep: oy + (D - dep) * S
    X = d.x
    def prect(x1, a, x2, b, cls):
        d.add(f'<rect class="{cls}" x="{X(x1):.2f}" y="{Y(b):.2f}" width="{(x2-x1)*S:.2f}" height="{(b-a)*S:.2f}"/>')
    def ext(dep, x_from, px):
        d.add(f'<line class="ext" x1="{X(x_from):.1f}" y1="{Y(dep):.1f}" x2="{px:.1f}" y2="{Y(dep):.1f}"/>')
    def dim_depth(a, b, px, label, side="right"):
        ya, yb2 = Y(a), Y(b)
        d.add(f'<line class="dim" x1="{px:.1f}" y1="{ya:.1f}" x2="{px:.1f}" y2="{yb2:.1f}" marker-start="url(#a)" marker-end="url(#a)"/>')
        tx = px + 14 if side == "right" else px - 6
        d.add(f'<text class="t" transform="translate({tx:.1f},{(ya+yb2)/2:.1f}) rotate(-90)" text-anchor="middle">{label}</text>')
    def dim_depth_text(a, b, px, label, small=False):
        ya, yb2 = Y(a), Y(b)                  # ya below yb2 on the page
        if small:                             # arrows outside, pointing in
            d.add(f'<line class="dim" x1="{px:.1f}" y1="{ya+14:.1f}" x2="{px:.1f}" y2="{ya:.1f}" marker-end="url(#a)"/>')
            d.add(f'<line class="dim" x1="{px:.1f}" y1="{yb2-14:.1f}" x2="{px:.1f}" y2="{yb2:.1f}" marker-end="url(#a)"/>')
        else:
            d.add(f'<line class="dim" x1="{px:.1f}" y1="{ya:.1f}" x2="{px:.1f}" y2="{yb2:.1f}" marker-start="url(#a)" marker-end="url(#a)"/>')
        d.text(px - 5, (ya + yb2) / 2 + 4, label, "t", "end")
    d.text(20, 24, f"Plan view, top removed, bench pushed in — 1 in = {S} px", "h", "start")
    d.add(f'<rect class="hid" x="{X(0):.1f}" y="{Y(D):.1f}" width="{W*S}" height="{D*S}"/>')
    # bench, then the frame over it: aprons sit directly above the lower rails
    prect(BX0, B_FRONT, BX0 + BW, B_BACK, "shelf")
    d.text(X(W / 2), Y(6.6) + 4, f"bench {frac(BW)} × {frac(BD)} (lid hinged at the back)", "n")
    prect(L1, F0, R0, F0 + AP_T, "wood"); prect(L1, D - OV - AP_T, R0, D - OV, "wood")
    prect(L0, F1, L0 + AP_T, B0, "wood"); prect(R1 - AP_T, F1, R1, B0, "wood")
    for x in (L0, R0):
        prect(x, F0, x + LEG, F1, "leg"); prect(x, B0, x + LEG, B1, "leg")
    d.dim_h(L0 + RAIL_T, R1 - RAIL_T, Y(10.4), f"{frac(R1 - L0 - 2 * RAIL_T)} between side rails (inner faces)")
    d.text(X(W / 2), Y(0) + 16, "FRONT (open: no lower front rail)", "n")
    # top rows
    d.dim_h(0, W, 42, f"{frac(W)} overall", pyo=Y(D))
    d.dim_h(0, OV, 68, frac(OV), pyo=Y(D))
    d.dim_h(OV, W - OV, 68, f"{frac(FR_W)} leg frame", pyo=Y(B1))
    d.dim_h(W - OV, W, 68, frac(OV), pyo=Y(D))
    # bottom rows
    yb = Y(0) + 30
    d.dim_h(L1, R0, yb, f"{frac(R0 - L1)} between legs", pyo=Y(F0), below=True)
    d.dim_h(BX0, BX0 + BW, yb + 28, f"{frac(BW)} bench, {frac(BX0 - L1)} clear each side", pyo=Y(B_FRONT), below=True)
    # right: overall and leg frame depth
    pr1, pr2 = X(W) + 24, X(W) + 54
    ext(0, W, pr1); ext(D, W, pr1)
    ext(F0, R1, pr2); ext(B1, R1, pr2)
    dim_depth(0, D, pr1, f"{frac(D)} overall")
    dim_depth(OV, D - OV, pr2, f"{frac(FR_D)} leg frame")
    # left: where the bench sits front to back
    pl = X(0) - 22
    ext(0, 0, pl); ext(D, 0, pl)
    ext(B_FRONT, BX0, pl); ext(B_BACK, BX0, pl)
    dim_depth_text(0, B_FRONT, pl, frac(B_FRONT), small=True)
    dim_depth(B_FRONT, B_BACK, pl, f"{frac(BD)} bench", side="left")
    dim_depth_text(B_BACK, D, pl, frac(D - B_BACK))
    yn = yb + 28 + 46
    d.text(X(0), yn, f"Dashed outline = top, {frac(W)} × {frac(D)} × {frac(TOP_T)}. Aprons (upper) and lower rails (below the bench top) are {frac(AP_T)} thick,", "n", "start")
    d.text(X(0), yn + 16, f"flush to the leg outer faces; each apron hides the rail under it. The bench stops against the back lower rail", "n", "start")
    d.text(X(0), yn + 32, f"(its back at {frac(B_BACK)} from the top's front edge) and passes between the legs and the side rails.", "n", "start")
    d.save(path, "Console with bench, plan view", EXTRA)


def bench(path):
    d = D2(560, 440, 120, 80, s=K)
    d.text(20, 24, f"Chest end section (looking from the side) — 1 in = {K} px", "h", "start")
    case_bot = LID_T + CASE_H
    by = case_bot - GROOVE_UP - BOT_T                            # bottom's top face
    # lid cleat seen beyond the cut (it sits 2″ in from the end)
    c0 = (BD - CLEAT_L) / 2
    d.rect(c0, LID_T, c0 + CLEAT_L, LID_T + CLEAT_T, "beyond")
    d.rect(0, 0, BD, LID_T, "face")                              # lid
    d.rect(0, LID_T, WALL, case_bot, "shelf")                    # front wall
    d.rect(BD - WALL, LID_T, BD, case_bot, "shelf")              # back wall
    d.rect(WALL - GROOVE_D, by, WALL, by + BOT_T, "groove")      # grooves
    d.rect(BD - WALL, by, BD - WALL + GROOVE_D, by + BOT_T, "groove")
    d.rect((BD - BOT_W) / 2, by, (BD + BOT_W) / 2, by + BOT_T, "wood")   # floating bottom
    d.rect(INSET, case_bot, INSET + PL_T, BH, "wood")            # plinth front
    d.rect(BD - INSET - PL_T, case_bot, BD - INSET, BH, "wood")  # plinth back
    _floor(d, -1, BD + 1, BH)
    d.add(f'<circle class="knuckle" cx="{d.x(BD):.1f}" cy="{d.y(LID_T):.1f}" r="3.5"/>')
    d.leader(d.x(BD) + 3, d.y(LID_T) - 3, d.x(BD) + 22, d.y(0) - 22, "piano hinge at the lid/case seam")
    d.text(d.x(0) + 4, d.y(0) - 8, "front", "n", "start")
    d.text(d.x(BD) - 4, d.y(0) - 8, "back", "n", "end")
    d.text(d.x(BD / 2), d.y(LID_T / 2) + 4, f"lid {frac(LID_T)}", "n")
    d.text(d.x(BD / 2), d.y(LID_T + CLEAT_T) + 13,
           f"lid cleat beyond, {frac(CLEAT_T)} × {frac(CLEAT_W)} × {frac(CLEAT_L)}", "n")
    d.text(d.x(BD / 2), d.y(LID_T + 3.6), f"interior ≈ {frac(IN_W)} × {frac(IN_D)} × {frac(IN_H)}", "n")
    d.text(d.x(BD / 2), d.y(LID_T + 4.6), f"(dovetailed {frac(WALL)} cherry case)", "n")
    d.dim_h(WALL, BD - WALL, d.y(LID_T + 7), f"{frac(IN_D)} inside")
    d.dim_h_small(0, WALL, d.y(LID_T + 9), f"{frac(WALL)} walls")
    d.text(d.x(BD / 2), d.y(by) - 22, f"bottom {frac(BOT_T)} × {frac(BOT_W)}, floating", "n")
    d.text(d.x(BD / 2), d.y(by) - 8, f"in {frac(GROOVE_D)} grooves, {frac(GROOVE_UP)} up from the edge", "n")
    d.text(d.x(BD / 2), d.y(BH - 0.75), f"plinth {frac(PL_T)} × {frac(PLINTH_H)}, inset {frac(INSET)}", "n")
    # top / left
    d.dim_h(0, BD, 52, f"{frac(BD)} deep", pyo=d.y(0))
    d.dim_v(0, BH, 66, f"{frac(BH)} total", pxo=d.x(0))
    # right: interior height (inner col), lid / case / plinth (outer col)
    pi, po = d.x(BD) + 40, d.x(BD) + 80
    d.ext_h(LID_T, BD - WALL, pi)
    d.ext_h(by, BD - WALL, pi)
    d.ext_h(0, BD, po)
    d.ext_h(LID_T, BD, po)
    d.ext_h(case_bot, BD, po)
    d.ext_h(BH, BD - INSET, po)
    d.dim_v(LID_T, by, pi, f"{frac(IN_H)} inside", left=False)
    d.dim_v_text(0, LID_T, po, f"{frac(LID_T)} lid")
    d.dim_v(LID_T, case_bot, po, f"{frac(CASE_H)} case", left=False)
    d.dim_v_text(case_bot, BH, po, f"{frac(PLINTH_H)} plinth")
    # below the floor: plinth inset and plinth-end length
    yr = d.y(BH) + 24
    d.ext_v(0, case_bot, yr + 4)
    d.ext_v(INSET, BH, yr + 4)
    d.dim_h_small(0, INSET, yr, f"{frac(INSET)} inset", side="left")
    d.dim_h(INSET, BD - INSET, yr + 26, f"{frac(BD - 2 * INSET)} plinth ends (outside)", pyo=d.y(BH), below=True)
    d.save(path, "Chest bench end section", EXTRA)


def chest_front(path):
    d = D2(800, 480, 100, 100, s=K)
    d.text(20, 24, f"Chest front elevation (dashed = hidden) — 1 in = {K} px", "h", "start")
    case_bot = LID_T + CASE_H
    by = case_bot - GROOVE_UP - BOT_T
    d.rect(INSET, case_bot, BW - INSET, BH, "wood")              # plinth front
    d.rect(0, LID_T, BW, case_bot, "shelf")                      # case front
    d.rect(0, LID_T, WALL, case_bot, "dt")                       # dovetailed corners
    d.rect(BW - WALL, LID_T, BW, case_bot, "dt")
    d.rect(0, 0, BW, LID_T, "face")                              # lid
    for x in (CLEAT_IN, BW - CLEAT_IN - CLEAT_W):                # lid cleats (hidden)
        d.rect(x, LID_T, x + CLEAT_W, LID_T + CLEAT_T, "hid")
    d.rect(WALL - GROOVE_D, by, BW - WALL + GROOVE_D, by + BOT_T, "hid")   # bottom (hidden)
    _floor(d, -1, BW + 1, BH)
    d.text(d.x(BW / 2), d.y(5.2), f"case front {frac(WALL)} × {frac(CASE_H)} × {frac(BW)}", "n")
    d.text(d.x(BW / 2), d.y(5.2) + 16, "through-dovetailed to the ends at both corners (hatched)", "n")
    d.text(d.x(BW / 2), d.y(case_bot + PLINTH_H / 2) + 4,
           f"plinth front {frac(PL_T)} × {frac(PLINTH_H)} × {frac(BW - 2 * INSET)}, mitered corners", "n")
    d.text(d.x(BW / 2), d.y(LID_T) + 14, f"cleats {frac(CLEAT_IN)} in from each end, run front to back", "n")
    # top rows
    d.dim_h(0, BW, 44, f"{frac(BW)} overall", pyo=d.y(0))
    d.dim_h(0, CLEAT_IN, 72, frac(CLEAT_IN), pyo=d.y(LID_T))
    d.dim_h(CLEAT_IN, CLEAT_IN + CLEAT_W, 72, "", pyo=d.y(LID_T))
    d.text(d.x(CLEAT_IN + CLEAT_W) + 6, 76, f"{frac(CLEAT_W)} cleat", "t", "start")
    d.dim_h(BW - CLEAT_IN, BW, 72, frac(CLEAT_IN), pyo=d.y(LID_T))
    # bottom length, just above it
    d.dim_h(WALL - GROOVE_D, BW - WALL + GROOVE_D, d.y(by) - 14,
            f"{frac(BOT_L)} bottom (hidden), {frac(GROOVE_D)} into each end groove", pyo=d.y(by))
    # left: total; right: lid / case / plinth
    d.dim_v(0, BH, 64, f"{frac(BH)} total", pxo=d.x(0))
    pr = d.x(BW) + 24
    d.ext_h(0, BW, pr); d.ext_h(LID_T, BW, pr); d.ext_h(case_bot, BW, pr); d.ext_h(BH, BW - INSET, pr)
    d.dim_v_text(0, LID_T, pr, f"{frac(LID_T)} lid")
    d.dim_v(LID_T, case_bot, pr, f"{frac(CASE_H)} case", left=False)
    d.dim_v_text(case_bot, BH, pr, f"{frac(PLINTH_H)} plinth")
    # below the floor
    yr = d.y(BH) + 24
    d.ext_v(0, case_bot, yr + 4)
    d.ext_v(INSET, BH, yr + 4)
    d.dim_h_small(0, INSET, yr, f"{frac(INSET)} inset", side="left")
    d.dim_h(INSET, BW - INSET, yr + 26, f"{frac(BW - 2 * INSET)} plinth front / back (outside)", pyo=d.y(BH), below=True)
    d.save(path, "Chest bench front elevation", EXTRA)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "..", "public", "static", "woodworking")
    os.makedirs(out, exist_ok=True)
    front(os.path.join(out, "bench-console-front.svg"))
    side(os.path.join(out, "bench-console-side.svg"))
    plan(os.path.join(out, "bench-console-plan.svg"))
    bench(os.path.join(out, "bench-console-bench.svg"))
    chest_front(os.path.join(out, "bench-console-chest-front.svg"))
    print("wrote 5 SVGs to", os.path.normpath(out))
