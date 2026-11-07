#!/usr/bin/env python3
"""True-scale SVGs for the Heartwood Shaker 3-drawer nightstand plan.

Usage: python3 tools/woodworking/nightstand_drawings.py
Writes static/static/woodworking/nightstand-{front,side,plan,apron}.svg
Geometry in inches. Stated: 24 W x 18 D x 28 H. Everything else is measured off the
maker's photo/drawing (see the plan page) -- edit constants here and re-run.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from modern_craftsman_drawings import Drawing

K = 16                          # px per inch for the three main views
W, D, H = 24, 18, 28            # overall (stated)
OV_END, OV_FB = 2.5, 1.25       # top overhang: ends (measured) / front-back (sibling model)
TOP_T = 1.0                     # est.
LEG = 1.5                       # est.
CASE_W, CASE_D = W - 2 * OV_END, D - 2 * OV_FB      # 19 x 15.5
OPEN_W = CASE_W - 2 * LEG                           # 16
DR_H, REV, RAIL = 6.0, 1 / 16, 0.75                 # drawer front, reveal, rail height
DR_W = OPEN_W - 2 * REV                             # 15 7/8
APRON_END, APRON_MID = 2.625, 1.625
LX0, LX1 = OV_END, OV_END + LEG                     # 2.5..4
RX0, RX1 = W - OV_END - LEG, W - OV_END             # 20..21.5
FD0, FD1 = OV_FB, OV_FB + LEG                       # 1.25..2.75
BD0, BD1 = D - OV_FB - LEG, D - OV_FB               # 15.25..16.75

# vertical stack (from top surface): top, then drawer openings
d1 = TOP_T + REV
r1 = d1 + DR_H + REV
d2 = r1 + RAIL + REV
r2 = d2 + DR_H + REV
d3 = r2 + RAIL + REV
OPEN_BOT = d3 + DR_H + REV                          # 20.875 -> 7 1/8 off floor


def _floor(d, x0, x1):
    d.add(f'<line class="floor" x1="{d.x(x0):.1f}" y1="{d.y(H):.1f}" x2="{d.x(x1):.1f}" y2="{d.y(H):.1f}"/>')


def front(path):
    d = Drawing(640, 650, 95, 100, s=K)
    d.text(20, 24, "Front elevation — 1 in = 16 px", "h", "start")
    d.rect(0, 0, W, TOP_T, "wood")
    d.rect(LX0, TOP_T, LX1, H, "leg"); d.rect(RX0, TOP_T, RX1, H, "leg")
    for y0 in (r1, r2):
        d.rect(LX1, y0, RX0, y0 + RAIL, "wood")
    for y0 in (d1, d2, d3):
        d.rect(LX1 + REV, y0, RX0 - REV, y0 + DR_H, "face")
        cx, cy = W / 2, y0 + DR_H / 2
        d.add(f'<circle class="pull" cx="{d.x(cx):.1f}" cy="{d.y(cy):.1f}" r="{0.625*K:.1f}"/>')
        d.text(d.x(cx), d.y(y0 + 1.1), "15⅞″ × 6″ front", "n")
        d.text(d.x(cx), d.y(cy + 1.45), "knob ≈ 1¼″ ⌀", "n")
    # arched apron
    xl, xr, xm = d.x(LX1), d.x(RX0), d.x(W / 2)
    yt, ye, yc = d.y(OPEN_BOT), d.y(OPEN_BOT + APRON_END), d.y(OPEN_BOT + 2 * (APRON_MID - 0.5 * APRON_END) + 0)  # placeholder
    # control point so the arc midpoint sits at the centre height
    ymid = OPEN_BOT + APRON_MID
    ctrl = d.y(2 * ymid - (OPEN_BOT + APRON_END))
    d.add(f'<path class="face" d="M{xl:.1f},{yt:.1f} L{xr:.1f},{yt:.1f} L{xr:.1f},{ye:.1f} Q{xm:.1f},{ctrl:.1f} {xl:.1f},{ye:.1f} Z"/>')
    d.text(xm, d.y(OPEN_BOT + 0.95), "arched apron: 2⅝″ ends, 1⅝″ centre", "n")
    _floor(d, -1, W + 1)
    d.dim_h(0, W, 42, "24″ overall", pyo=d.y(0))
    d.dim_h(0, OV_END, 68, "2½″", pyo=d.y(0))
    d.dim_h(OV_END, W - OV_END, 68, "19″ case", pyo=d.y(TOP_T))
    d.dim_h(W - OV_END, W, 68, "2½″", pyo=d.y(0))
    d.dim_v(0, H, 52, "28″ overall", pxo=d.x(0))
    px = d.x(W) + 22
    d.dim_v(0, TOP_T, px, "1″", pxo=d.x(W))
    for y0 in (d1, d2, d3):
        d.dim_v(y0, y0 + DR_H, px, "6″", pxo=d.x(RX1))
    for y0 in (r1, r2):
        d.dim_v(y0 + REV, y0 + RAIL + REV, px, "", pxo=d.x(RX1))
    d.text(px + 14, d.y(r1 + 0.4) + 3, "¾″", "t", "start")
    d.text(px + 14, d.y(r2 + 0.4) + 3, "¾″", "t", "start")
    d.dim_v(OPEN_BOT, H, px + 44, "7⅛″ floor to opening", pxo=d.x(RX1))
    yb = d.y(H) + 28
    d.dim_h(LX0, LX1, yb, "1½″", pyo=d.y(H), below=True)
    d.dim_h(LX1, RX0, yb, "16″ opening", pyo=d.y(H), below=True)
    d.dim_h(RX0, RX1, yb, "1½″", pyo=d.y(H), below=True)
    d.save(path, "Heartwood Shaker nightstand, front elevation")


def side(path):
    d = Drawing(580, 650, 95, 100, s=K)
    d.text(20, 24, "Side elevation — 1 in = 16 px", "h", "start")
    d.rect(0, 0, D, TOP_T, "wood")
    d.rect(FD0, TOP_T, FD1, H, "leg"); d.rect(BD0, TOP_T, BD1, H, "leg")
    top_rail_h, mun = 1.5, 1.0
    p_top = TOP_T + top_rail_h
    d.rect(FD1, TOP_T, BD0, p_top, "wood")                               # top side rail
    span = BD0 - FD1                                                     # 12.5
    pw = (span - mun) / 2                                                # each visible panel
    d.rect(FD1, p_top, FD1 + pw, OPEN_BOT, "face")                       # panel 1
    d.rect(FD1 + pw, p_top, FD1 + pw + mun, OPEN_BOT, "wood")            # centre muntin
    d.rect(FD1 + pw + mun, p_top, BD0, OPEN_BOT, "face")                 # panel 2
    xl, xr, xm = d.x(FD1), d.x(BD0), d.x((FD1 + BD0) / 2)
    ymid = OPEN_BOT + APRON_MID
    ctrl = d.y(2 * ymid - (OPEN_BOT + APRON_END))
    d.add(f'<path class="wood" d="M{xl:.1f},{d.y(OPEN_BOT):.1f} L{xr:.1f},{d.y(OPEN_BOT):.1f} L{xr:.1f},{d.y(OPEN_BOT + APRON_END):.1f} Q{xm:.1f},{ctrl:.1f} {xl:.1f},{d.y(OPEN_BOT + APRON_END):.1f} Z"/>')
    d.text(d.x(9), d.y(TOP_T + top_rail_h / 2) + 4, "top side rail 1½″", "n")
    d.text(d.x(FD1 + pw / 2), d.y(11), "panel", "n")
    d.text(d.x(FD1 + pw + mun + pw / 2), d.y(11), "panel", "n")
    d.text(d.x(FD1 + pw + mun + 0.3), d.y(16), "◀ muntin 1″", "n", "start")
    d.text(d.x(9), d.y(OPEN_BOT + 1.0) + 4, "arched bottom rail", "n")
    _floor(d, -1, D + 1)
    d.text(d.x(0.4), d.y(H) - 8, "front", "n", "start")
    d.dim_h(0, D, 42, "18″ overall", pyo=d.y(0))
    d.dim_h(0, OV_FB, 68, "1¼″", pyo=d.y(0))
    d.dim_h(OV_FB, D - OV_FB, 68, "15½″ case", pyo=d.y(TOP_T))
    d.dim_h(D - OV_FB, D, 68, "1¼″", pyo=d.y(0))
    d.dim_v(0, H, 52, "28″ overall", pxo=d.x(0))
    yb = d.y(H) + 28
    d.dim_h(FD0, FD1, yb, "1½″", pyo=d.y(H), below=True)
    d.dim_h(FD1, BD0, yb, "12½″ between legs", pyo=d.y(H), below=True)
    d.dim_h(BD0, BD1, yb, "1½″", pyo=d.y(H), below=True)
    d.save(path, "Heartwood Shaker nightstand, side elevation")


def plan(path):
    oy = 100
    d = Drawing(700, 470, 95, oy, s=K)
    Y = lambda dep: oy + (D - dep) * K
    X = d.x
    def prect(x1, a, x2, b, cls):
        d.add(f'<rect class="{cls}" x="{X(x1):.2f}" y="{Y(b):.2f}" width="{(x2-x1)*K:.2f}" height="{(b-a)*K:.2f}"/>')
    d.text(20, 24, "Plan view, top removed — 1 in = 16 px", "h", "start")
    d.add(f'<rect class="hid" x="{X(0):.1f}" y="{Y(D):.1f}" width="{W*K}" height="{D*K}"/>')
    # side frames (3/4 thick, flush outside), back, front rails
    prect(LX0, FD1, LX0 + 0.75, BD0, "wood"); prect(RX1 - 0.75, FD1, RX1, BD0, "wood")
    prect(LX1, BD1 - 0.75, RX0, BD1, "wood")
    prect(LX1, FD0, RX0, FD0 + 0.75, "wood")
    # slide spacers (3/4) on the side frames
    prect(LX0 + 0.75, FD0 + 0.75, LX1, FD0 + 0.75 + 12, "spacer"); prect(RX0, FD0 + 0.75, RX1 - 0.75, FD0 + 0.75 + 12, "spacer")
    # drawer: front + dashed box (15 wide x 12 long)
    cx = W / 2
    prect(LX1 + REV, FD0, RX0 - REV, FD0 + 0.75, "face")
    d.add(f'<rect class="hid" x="{X(cx-7.5):.1f}" y="{Y(FD0+0.75+12):.1f}" width="{15*K}" height="{12*K}"/>')
    d.text(X(cx), Y(8), "drawer box 15″ wide × 12″ long (dashed)", "n")
    d.text(X(cx), Y(7), "3 stacked, each on side-mount slides", "n")
    for x in (LX0, RX0):
        prect(x, FD0, x + LEG, FD1, "leg"); prect(x, BD0, x + LEG, BD1, "leg")
    d.text(X(cx), Y(0) + 16, "FRONT", "n")
    d.text(X(0), Y(0) + 46, "Dashed outline = top, 24″ × 18″ × 1″, floating on buttons.", "n", "start")
    d.text(X(0), Y(0) + 62, "Side frames are ¾″ thick, flush to the leg outer faces; grey = ¾″ slide spacers.", "n", "start")
    d.dim_h(0, W, 42, "24″ overall", pyo=Y(D))
    d.dim_h(0, OV_END, 68, "2½″", pyo=Y(D))
    d.dim_h(OV_END, W - OV_END, 68, "19″ case", pyo=Y(BD1))
    d.dim_h(W - OV_END, W, 68, "2½″", pyo=Y(D))
    def dim_depth(a, b, px, label):
        ya, yb2 = Y(a), Y(b)
        d.add(f'<line class="dim" x1="{px}" y1="{ya:.1f}" x2="{px}" y2="{yb2:.1f}" marker-start="url(#a)" marker-end="url(#a)"/>')
        d.add(f'<text class="t" transform="translate({px+14},{(ya+yb2)/2:.1f}) rotate(-90)" text-anchor="middle">{label}</text>')
    dim_depth(0, D, X(W) + 24, "18″ overall")
    dim_depth(OV_FB, D - OV_FB, X(W) + 54, "15½″ case")
    d.save(path, "Heartwood Shaker nightstand, plan view")


def apron(path):
    P = 24
    d = Drawing(640, 300, 80, 110, s=P)
    d.text(20, 24, "Front apron blank — 1 in = 24 px", "h", "start")
    R = (16 ** 2) / (8 * 1.0) + 0.5   # 32.5
    x0, x1 = 1.0, 17.0                 # shoulders
    path_d = (f'M{d.x(x0):.1f},{d.y(0):.1f} L{d.x(x1):.1f},{d.y(0):.1f} L{d.x(x1):.1f},{d.y(APRON_END):.1f} '
              f'A{R*P:.1f},{R*P:.1f} 0 0 0 {d.x(x0):.1f},{d.y(APRON_END):.1f} Z')
    d.add(f'<path class="face" d="{path_d}"/>')
    for a, b in ((0, 1.0), (17.0, 18.0)):
        d.add(f'<rect class="hid" x="{d.x(a):.1f}" y="{d.y(0.4375):.1f}" width="{(b-a)*P:.1f}" height="{1.75*P:.1f}"/>')
    d.text(d.x(9), d.y(0.8), "front apron ¾″ thick, cherry", "n")
    d.text(d.x(0.5), d.y(2.65) + 6, "tenon", "n")
    d.text(d.x(17.5), d.y(2.65) + 6, "tenon", "n")
    d.dim_h(0, 18, 60, "18″ cut length (1″ tenons each end)", pyo=d.y(0))
    d.dim_h(x0, x1, 86, "16″ shoulder to shoulder = drawer opening", pyo=d.y(0))
    d.dim_v(0, APRON_END, d.x(0) - 24, "2⅝″ at ends", pxo=d.x(x0))
    d.dim_v(0, APRON_MID, d.x(9), "", pxo=None)
    d.text(d.x(9) + 8, d.y(APRON_MID / 2) + 38, "1⅝″ at centre", "t", "start")
    d.text(d.x(9), d.y(APRON_END) + 70, f"Arc: 1″ rise over a 16″ chord → radius {R:g}″. Scribe it with a thin batten sprung through the three points,", "n")
    d.text(d.x(9), d.y(APRON_END) + 86, "or strike it with a trammel. Tenons 1″ long × ~1¾″ wide × 5/16″ thick (est.), centred.", "n")
    d.save(path, "Heartwood Shaker nightstand, front apron blank")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "..", "static", "static", "woodworking")
    os.makedirs(out, exist_ok=True)
    front(os.path.join(out, "nightstand-front.svg"))
    side(os.path.join(out, "nightstand-side.svg"))
    plan(os.path.join(out, "nightstand-plan.svg"))
    apron(os.path.join(out, "nightstand-apron.svg"))
    print("wrote 4 SVGs to", os.path.normpath(out))
