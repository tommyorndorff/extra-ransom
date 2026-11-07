#!/usr/bin/env python3
"""True-scale SVGs for the Cherry Console + Slide-Under Chest Bench plan.

Usage: python3 tools/woodworking/bench_console_drawings.py
Writes static/static/woodworking/bench-console-{front,side,plan,bench}.svg
Geometry in inches. Edit the constants and re-run.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from modern_craftsman_drawings import Drawing

# console
W, D, H = 42, 15, 35
OV = 1.0
TOP_T, LEG = 0.75, 1.5
AP_H, RAIL_H, RAIL_TOP = 3.5, 2.5, 9.25
FR_W, FR_D = W - 2 * OV, D - 2 * OV                 # 40 x 13
L0, L1 = OV, OV + LEG                               # 1..2.5
R0, R1 = W - OV - LEG, W - OV                       # 39.5..41
F0, F1 = OV, OV + LEG                               # 1..2.5   (front legs, depth)
B0, B1 = D - OV - LEG, D - OV                       # 12.5..14 (back legs, depth)
APRON_BOT = TOP_T + AP_H                            # 4.25 from top surface -> 30.75 above floor
# bench
BW, BD, BH = 36.0, 13.0, 17.0
LID_T, PLINTH_H, INSET = 1.0, 2.25, 0.375
CASE_H = BH - LID_T - PLINTH_H                      # 13.75
BACK_STOP = D - OV - 0.75                           # inner face of back rail: 13.25
BX0 = (W - BW) / 2                                  # 3.0
B_FRONT, B_BACK = BACK_STOP - BD, BACK_STOP         # 0.25..13.25 (depth)
LID_Y0 = H - BH                                     # lid top, from top surface = 18
CASE_Y0, PLINTH_Y0 = LID_Y0 + LID_T, LID_Y0 + LID_T + CASE_H


def _floor(d, a, b):
    d.add(f'<line class="floor" x1="{d.x(a):.1f}" y1="{d.y(H):.1f}" x2="{d.x(b):.1f}" y2="{d.y(H):.1f}"/>')


def front(path):
    d = Drawing(720, 650, 95, 100, s=12)
    d.text(20, 24, "Front elevation, bench pushed in — 1 in = 12 px", "h", "start")
    d.rect(0, 0, W, TOP_T, "wood")
    d.rect(L0, TOP_T, L1, H, "leg"); d.rect(R0, TOP_T, R1, H, "leg")
    d.rect(L1, TOP_T, R0, APRON_BOT, "face")
    # bench
    d.rect(BX0 + INSET, PLINTH_Y0, BX0 + BW - INSET, H, "wood")
    d.rect(BX0, CASE_Y0, BX0 + BW, PLINTH_Y0, "shelf")
    d.rect(BX0, LID_Y0, BX0 + BW, CASE_Y0, "face")
    d.text(d.x(W / 2), d.y(CASE_Y0 + 6.5), "blanket chest bench", "n")
    d.text(d.x(W / 2), d.y(CASE_Y0 + 8.2), "36″ × 13″ × 17″", "n")
    d.text(d.x(W / 2), d.y(TOP_T + 1.9) + 4, "apron ¾″ × 3½″", "n")
    d.text(d.x(W / 2), d.y(10), "open space above the lid", "n")
    _floor(d, -1, W + 1)
    d.dim_h(0, W, 42, "42″ overall", pyo=d.y(0))
    d.dim_h(0, OV, 68, "1″", pyo=d.y(0))
    d.dim_h(OV, W - OV, 68, "40″ leg frame", pyo=d.y(TOP_T))
    d.dim_h(W - OV, W, 68, "1″", pyo=d.y(0))
    d.dim_v(0, H, 52, "35″ overall", pxo=d.x(0))
    px = d.x(W) + 24
    d.dim_v(APRON_BOT, H, px, "30¾″ clear under apron", pxo=d.x(R1))
    d.dim_v(LID_Y0, H, px + 44, "17″ seat height", pxo=d.x(BX0 + BW))
    d.dim_v(APRON_BOT, LID_Y0, px + 88, "13¾″ above lid", pxo=d.x(BX0 + BW))
    yb = d.y(H) + 28
    d.dim_h(L0, L1, yb, "1½″", pyo=d.y(H), below=True)
    d.dim_h(L1, R0, yb, "37″ between legs", pyo=d.y(H), below=True)
    d.dim_h(R0, R1, yb, "1½″", pyo=d.y(H), below=True)
    d.dim_h(BX0, BX0 + BW, yb + 28, "36″ bench — ½″ clear each side", pyo=None, below=True)
    d.save(path, "Console with bench, front elevation")


def side(path):
    d = Drawing(660, 650, 95, 100, s=12)
    d.text(20, 24, "Side elevation, lid open to vertical — 1 in = 12 px", "h", "start")
    d.rect(0, 0, D, TOP_T, "wood")
    d.rect(F0, TOP_T, F1, H, "leg"); d.rect(B0, TOP_T, B1, H, "leg")
    d.rect(F1, TOP_T, B0, APRON_BOT, "face")
    ry = H - RAIL_TOP
    # bench (seen through the open side)
    d.rect(B_FRONT + INSET, PLINTH_Y0, B_BACK - INSET, H, "wood")
    d.rect(B_FRONT, CASE_Y0, B_BACK, PLINTH_Y0, "shelf")
    d.rect(B_FRONT, LID_Y0, B_BACK, CASE_Y0, "face")
    d.rect(F1, ry, B0, ry + RAIL_H, "wood")      # side lower rail (in front of bench, outside it)
    # back lower rail / stop (hidden, dashed) and felt
    d.add(f'<rect class="hid" x="{d.x(B_BACK):.1f}" y="{d.y(ry):.1f}" width="{0.75*12:.1f}" height="{RAIL_H*12:.1f}"/>')
    d.text(d.x(7.8), d.y(ry + RAIL_H / 2) + 4, "side rail", "n")
    # lid open to vertical at the back hinge
    hx = B_BACK
    d.add(f'<rect class="hid" x="{d.x(hx-LID_T):.1f}" y="{d.y(LID_Y0-BD):.1f}" width="{LID_T*12:.1f}" height="{BD*12:.1f}"/>')
    # arc traced by the lid's front edge: centre (hx, LID_Y0), radius BD
    x1, y1 = d.x(B_FRONT), d.y(LID_Y0)
    x2, y2 = d.x(hx), d.y(LID_Y0 - BD)
    d.add(f'<path class="hid" d="M{x1:.1f},{y1:.1f} A{BD*12:.1f},{BD*12:.1f} 0 0 1 {x2:.1f},{y2:.1f}"/>')
    d.text(d.x(8.8), d.y(LID_Y0 - 6.0), "lid front edge", "n")
    d.text(d.x(8.8), d.y(LID_Y0 - 6.0) + 14, "path (hinge at back)", "n")
    d.text(d.x(7), d.y(TOP_T + 1.9) + 4, "side apron", "n")
    _floor(d, -1, D + 1)
    d.text(d.x(0.2), d.y(H) - 8, "front", "n", "start")
    d.dim_h(0, D, 42, "15″ overall", pyo=d.y(0))
    d.dim_h(0, OV, 68, "1″", pyo=d.y(0))
    d.dim_h(OV, D - OV, 68, "13″ leg frame", pyo=d.y(TOP_T))
    d.dim_h(D - OV, D, 68, "1″", pyo=d.y(0))
    d.dim_v(0, H, 52, "35″ overall", pxo=d.x(0))
    px = d.x(D) + 28
    d.dim_v(LID_Y0, H, px, "17″ seat height", pxo=d.x(B_BACK))
    d.dim_v(LID_Y0 - BD, LID_Y0, px + 44, "13″ lid", pxo=d.x(B_BACK))
    d.dim_v(APRON_BOT, LID_Y0 - BD, px + 88, "¾″ to spare", pxo=d.x(B1))
    yb = d.y(H) + 28
    d.dim_h(B_FRONT, B_BACK, yb, "13″ bench depth; front sits ¼″ behind the top edge", pyo=d.y(H), below=True)
    d.save(path, "Console with bench, side elevation with lid open")


def plan(path):
    oy = 100
    d = Drawing(700, 440, 95, oy, s=12)
    Y = lambda dep: oy + (D - dep) * 12
    X = d.x
    def prect(x1, a, x2, b, cls):
        d.add(f'<rect class="{cls}" x="{X(x1):.2f}" y="{Y(b):.2f}" width="{(x2-x1)*12:.2f}" height="{(b-a)*12:.2f}"/>')
    d.text(20, 24, "Plan view, top removed, bench pushed in — 1 in = 12 px", "h", "start")
    d.add(f'<rect class="hid" x="{X(0):.1f}" y="{Y(D):.1f}" width="{W*12}" height="{D*12}"/>')
    # lower rails (below the bench top): two sides + back
    prect(L0, F1, L0 + 0.75, B0, "wood"); prect(R1 - 0.75, F1, R1, B0, "wood")
    prect(L1, D - OV - 0.75, R0, D - OV, "wood")
    # bench
    prect(BX0, B_FRONT, BX0 + BW, B_BACK, "shelf")
    d.text(X(W / 2), Y(6.6) + 4, "bench 36″ × 13″ (lid hinged at the back)", "n")
    # upper frame over the rails: aprons
    prect(L1, F0, R0, F0 + 0.75, "wood"); prect(L1, D - OV - 0.75, R0, D - OV, "wood")
    prect(L0, F1, L0 + 0.75, B0, "wood"); prect(R1 - 0.75, F1, R1, B0, "wood")
    for x in (L0, R0):
        prect(x, F0, x + LEG, F1, "leg"); prect(x, B0, x + LEG, B1, "leg")
    d.text(X(W / 2), Y(0) + 16, "FRONT (open: no lower front rail)", "n")
    d.text(X(0), Y(0) + 62, "Dashed outline = top, 42″ × 15″ × ¾″. Aprons (upper) and lower rails (below the bench top) are ¾″ thick,", "n", "start")
    d.text(X(0), Y(0) + 78, "flush to the leg outer faces. The bench stops against the back lower rail and passes between the legs (37″)", "n", "start")
    d.text(X(0), Y(0) + 94, "and the side rails (38½″ apart).", "n", "start")
    d.dim_h(0, W, 42, "42″ overall", pyo=Y(D))
    d.dim_h(0, OV, 68, "1″", pyo=Y(D))
    d.dim_h(OV, W - OV, 68, "40″ leg frame", pyo=Y(B1))
    d.dim_h(W - OV, W, 68, "1″", pyo=Y(D))
    yb = Y(0) + 30
    d.dim_h(L1, R0, yb, "37″ between legs", pyo=Y(F0), below=True)
    def dim_depth(a, b, px, label):
        ya, yb2 = Y(a), Y(b)
        d.add(f'<line class="dim" x1="{px}" y1="{ya:.1f}" x2="{px}" y2="{yb2:.1f}" marker-start="url(#a)" marker-end="url(#a)"/>')
        d.add(f'<text class="t" transform="translate({px+14},{(ya+yb2)/2:.1f}) rotate(-90)" text-anchor="middle">{label}</text>')
    dim_depth(0, D, X(W) + 24, "15″ overall")
    dim_depth(OV, D - OV, X(W) + 54, "13″ leg frame")
    d.save(path, "Console with bench, plan view")


def bench(path):
    K = 16
    d = Drawing(640, 560, 120, 80, s=K)
    d.text(20, 24, "Bench end section (looking from the side) — 1 in = 16 px", "h", "start")
    wall = 0.75
    d.rect(0, 0, BD, LID_T, "face")                              # lid
    d.rect(0, LID_T, wall, LID_T + CASE_H, "shelf")              # front wall
    d.rect(BD - wall, LID_T, BD, LID_T + CASE_H, "shelf")        # back wall
    by = LID_T + CASE_H - 0.25 - 0.5
    d.rect(wall - 0.25, by, BD - wall + 0.25, by + 0.5, "wood")  # floating bottom in ¼″ grooves
    d.rect(INSET, LID_T + CASE_H, INSET + wall, BH, "wood")      # plinth front
    d.rect(BD - INSET - wall, LID_T + CASE_H, BD - INSET, BH, "wood")  # plinth back
    d.add(f'<line class="floor" x1="{d.x(-1):.1f}" y1="{d.y(BH):.1f}" x2="{d.x(BD+1):.1f}" y2="{d.y(BH):.1f}"/>')
    d.add(f'<rect class="pull" x="{d.x(BD-0.25):.1f}" y="{d.y(0.15):.1f}" width="{0.5*K:.1f}" height="{0.7*K:.1f}"/>')
    d.text(d.x(BD) + 36, d.y(0.5) + 4, "piano hinge", "n", "start")
    d.text(d.x(BD / 2), d.y(LID_T / 2) + 4, "lid 1″", "n")
    d.text(d.x(BD / 2), d.y(by) - 8, "½″ bottom, floating in ¼″ grooves", "n")
    d.text(d.x(BD / 2), d.y(LID_T + 3.5), "interior ≈ 34½″ × 11½″ × 13¼″", "n")
    d.text(d.x(BD / 2), d.y(LID_T + 4.7), "(dovetailed ¾″ cherry case)", "n")
    d.text(d.x(BD / 2), d.y(BH) - 8 - 0, "", "n")
    d.text(d.x(BD / 2), d.y(BH - 0.75), "plinth ¾″ × 2¼″, inset ⅜″", "n")
    d.text(d.x(0.1), d.y(BH) + 18, "front", "n", "start")
    d.dim_h(0, BD, 52, "13″ deep", pyo=d.y(0))
    d.dim_v(0, BH, 66, "17″ total", pxo=d.x(0))
    px = d.x(BD) + 130
    d.dim_v(0, LID_T, px, "1″ lid", pxo=d.x(BD))
    d.dim_v(LID_T, LID_T + CASE_H, px, "13¾″ case", pxo=d.x(BD))
    d.dim_v(LID_T + CASE_H, BH, px, "2¼″ plinth", pxo=d.x(BD - INSET))
    d.save(path, "Chest bench end section")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "..", "static", "static", "woodworking")
    os.makedirs(out, exist_ok=True)
    front(os.path.join(out, "bench-console-front.svg"))
    side(os.path.join(out, "bench-console-side.svg"))
    plan(os.path.join(out, "bench-console-plan.svg"))
    bench(os.path.join(out, "bench-console-bench.svg"))
    print("wrote 4 SVGs to", os.path.normpath(out))
