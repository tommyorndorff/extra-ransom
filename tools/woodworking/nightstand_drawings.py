#!/usr/bin/env python3
"""True-scale SVGs for the Heartwood Shaker 3-drawer nightstand plan.

Usage: python3 tools/woodworking/nightstand_drawings.py
Writes static/static/woodworking/nightstand-{front,side,plan,legs,apron}.svg
Geometry in inches. Stated: 24 W x 18 D x 28 H. Everything else is measured off the
maker's photo/drawing (see the plan page) -- edit constants here and re-run.
Labels are built from the constants with frac(), so the drawings follow them.
"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from modern_craftsman_drawings import Drawing, frac

K = 16                          # px per inch for the main views
P = 24                          # px per inch for the arched-rail blanks
W, D, H = 24, 18, 28            # overall (stated)
OV_END, OV_FB = 2.5, 1.25       # top overhang: ends (measured) / front-back (sibling model)
TOP_T = 1.0                     # est.
LEG = 1.5                       # est.
LEG_L = H - TOP_T                                   # 27
CASE_W, CASE_D = W - 2 * OV_END, D - 2 * OV_FB      # 19 x 15.5
OPEN_W = CASE_W - 2 * LEG                           # 16
DR_H, REV, RAIL = 6.0, 1 / 16, 0.75                 # drawer front, reveal, rail height
DR_W = OPEN_W - 2 * REV                             # 15 7/8
FRONT_T = 0.75                                      # drawer front thickness
KNOB = 1.25
APRON_END, APRON_MID = 2.625, 1.625                 # arched rails: height at ends / centre
TOP_RAIL = 1.5                                      # top side rails and back top rail
MUNTIN = 1.0
FRAME_T = 0.75                                      # rails/aprons, flush to leg outer faces
GROOVE, PLAY = 0.375, 0.125                         # side-panel groove depth; total play
BACK_GROOVE = 0.25                                  # back-panel groove (from the 16 3/8 width)
TENON, TEN_W, TEN_T = 1.0, 1.75, 5 / 16             # arched-rail tenons (est.)
SPACER_T, SPACER_L, SPACER_W = 0.75, 12.0, 2.0
SLIDE_CLR = 0.5
BOX_W, BOX_L = OPEN_W - 2 * SLIDE_CLR, 12.0         # 15 x 12
LX0, LX1 = OV_END, OV_END + LEG                     # 2.5..4
RX0, RX1 = W - OV_END - LEG, W - OV_END             # 20..21.5
FD0, FD1 = OV_FB, OV_FB + LEG                       # 1.25..2.75
BD0, BD1 = D - OV_FB - LEG, D - OV_FB               # 15.25..16.75
SIDE_SPAN = BD0 - FD1                               # 12.5 between legs (side)

# vertical stack (from top surface): top, then drawer openings
d1 = TOP_T + REV
r1 = d1 + DR_H + REV
d2 = r1 + RAIL + REV
r2 = d2 + DR_H + REV
d3 = r2 + RAIL + REV
OPEN_BOT = d3 + DR_H + REV                          # 20.875 -> 7 1/8 off floor
STACK = OPEN_BOT - TOP_T                            # 19 7/8
P_TOP = TOP_T + TOP_RAIL                            # top of side panels' opening
PANEL_OPEN_H = OPEN_BOT - P_TOP                     # 18 3/8 (also muntin length)
PANEL_OPEN_W = (SIDE_SPAN - MUNTIN) / 2             # 5 3/4
PANEL_W = PANEL_OPEN_W + 2 * GROOVE - PLAY          # 6 3/8
PANEL_H = PANEL_OPEN_H + 2 * GROOVE - PLAY          # 19
BACK_PANEL_W = OPEN_W + 2 * BACK_GROOVE - PLAY      # 16 3/8
BACK_PANEL_H = PANEL_OPEN_H + 2 * BACK_GROOVE - PLAY  # 18 3/4

EXTRA = """<style>
  .sub{font:600 12px 'Helvetica Neue',Arial,sans-serif;fill:#222}
</style>"""


def arc_radius(chord, rise):
    return chord ** 2 / (8 * rise) + rise / 2


def r_label(R):
    exact = abs(R * 16 - round(R * 16)) < 1e-6
    return ("" if exact else "≈ ") + frac(R)


def arch_path(d, x0, x1, y0, end_h, mid_h):
    """Closed outline of an arched rail between x0 and x1 (inches), top at y0:
    straight top, ends end_h tall, true circular arc rising to mid_h at centre."""
    R = arc_radius(x1 - x0, end_h - mid_h) * d.s
    return (f'M{d.x(x0):.1f},{d.y(y0):.1f} L{d.x(x1):.1f},{d.y(y0):.1f} '
            f'L{d.x(x1):.1f},{d.y(y0 + end_h):.1f} '
            f'A{R:.1f},{R:.1f} 0 0 0 {d.x(x0):.1f},{d.y(y0 + end_h):.1f} Z')


def dim_v_small(d, y1, y2, px, label, pxo=None, side="left"):
    """Vertical dim for a span too short for inside arrows: arrows outside, label beside."""
    a, b = d.y(y1), d.y(y2)
    if pxo is not None:
        for yy in (a, b):
            d.add(f'<line class="ext" x1="{px:.1f}" y1="{yy:.1f}" x2="{pxo:.1f}" y2="{yy:.1f}"/>')
    d.add(f'<line class="dim" x1="{px:.1f}" y1="{a-14:.1f}" x2="{px:.1f}" y2="{a:.1f}" marker-end="url(#a)"/>')
    d.add(f'<line class="dim" x1="{px:.1f}" y1="{b+14:.1f}" x2="{px:.1f}" y2="{b:.1f}" marker-end="url(#a)"/>')
    if side == "left":
        d.text(px - 5, (a + b) / 2 + 4, label, "t", "end")
    else:
        d.text(px + 5, (a + b) / 2 + 4, label, "t", "start")


def _floor(d, x0, x1):
    d.add(f'<line class="floor" x1="{d.x(x0):.1f}" y1="{d.y(H):.1f}" x2="{d.x(x1):.1f}" y2="{d.y(H):.1f}"/>')


def front(path):
    d = Drawing(620, 650, 95, 100, s=K)
    d.text(20, 24, "Front elevation — 1 in = 16 px", "h", "start")
    d.rect(0, 0, W, TOP_T, "wood")
    d.rect(LX0, TOP_T, LX1, H, "leg"); d.rect(RX0, TOP_T, RX1, H, "leg")
    for y0 in (r1, r2):
        d.rect(LX1, y0, RX0, y0 + RAIL, "wood")
    for y0 in (d1, d2, d3):
        d.rect(LX1 + REV, y0, RX0 - REV, y0 + DR_H, "face")
        cx, cy = W / 2, y0 + DR_H / 2
        d.add(f'<circle class="pull" cx="{d.x(cx):.1f}" cy="{d.y(cy):.1f}" r="{KNOB/2*K:.1f}"/>')
        d.text(d.x(cx), d.y(y0 + 1.1), f"{frac(DR_W)} × {frac(DR_H)} front", "n")
        d.text(d.x(cx), d.y(cy + 1.45), f"knob ≈ {frac(KNOB)} ⌀", "n")
    d.add(f'<path class="face" d="{arch_path(d, LX1, RX0, OPEN_BOT, APRON_END, APRON_MID)}"/>')
    d.text(d.x(W / 2), d.y(OPEN_BOT + 0.95),
           f"arched apron: {frac(APRON_END)} ends, {frac(APRON_MID)} centre", "n")
    _floor(d, -1, W + 1)
    # top: overall and overhangs
    d.dim_h(0, W, 42, f"{frac(W)} overall", pyo=d.y(0))
    d.dim_h(0, OV_END, 68, frac(OV_END), pyo=d.y(0))
    d.dim_h(OV_END, W - OV_END, 68, f"{frac(CASE_W)} case", pyo=d.y(TOP_T))
    d.dim_h(W - OV_END, W, 68, frac(OV_END), pyo=d.y(0))
    d.dim_v(0, H, 52, f"{frac(H)} overall", pxo=d.x(0))
    # rails between drawers (left, outside the left leg)
    for y0 in (r1, r2):
        dim_v_small(d, y0, y0 + RAIL, d.x(0) + 14, f"{frac(RAIL)} rail", pxo=d.x(LX1))
    # drawer fronts (right, column 1)
    c1 = d.x(W) + 22
    for y0 in (d1, d2, d3):
        d.dim_v(y0, y0 + DR_H, c1, frac(DR_H), pxo=d.x(RX0), left=False)
    # height chain (right, column 2): top + drawer stack + floor = overall
    c2 = c1 + 44
    d.dim_v_text(0, TOP_T, c2, f"{frac(TOP_T)} top", pxo=d.x(W))
    d.add(f'<line class="ext" x1="{c2:.1f}" y1="{d.y(OPEN_BOT):.1f}" x2="{d.x(RX0):.1f}" y2="{d.y(OPEN_BOT):.1f}"/>')
    d.dim_v(TOP_T, OPEN_BOT, c2, f"{frac(STACK)} drawer stack", left=False)
    d.dim_v(OPEN_BOT, H, c2, f"{frac(H - OPEN_BOT)} to floor", pxo=d.x(W + 1), left=False)
    # floor clearance under the apron
    d.dim_v(OPEN_BOT + APRON_END, H, d.x(LX1) + 8, frac(H - OPEN_BOT - APRON_END),
            pxo=d.x(LX1), left=False)
    d.dim_v(OPEN_BOT + APRON_MID, H, d.x(W / 2), f"{frac(H - OPEN_BOT - APRON_MID)} at centre", left=False)
    yb = d.y(H) + 28
    d.dim_h(LX0, LX1, yb, frac(LEG), pyo=d.y(H), below=True)
    d.dim_h(LX1, RX0, yb, f"{frac(OPEN_W)} opening", pyo=d.y(H), below=True)
    d.dim_h(RX0, RX1, yb, frac(LEG), pyo=d.y(H), below=True)
    d.text(d.x(W / 2), yb + 40,
           f"{frac(REV)} reveal all round each front · rails {frac(RAIL)} × {frac(RAIL)} · legs {frac(LEG_L)} long", "n")
    d.save(path, "Heartwood Shaker nightstand, front elevation")


def side(path):
    d = Drawing(540, 650, 95, 100, s=K)
    d.text(20, 24, "Side elevation — 1 in = 16 px", "h", "start")
    d.rect(0, 0, D, TOP_T, "wood")
    d.rect(FD0, TOP_T, FD1, H, "leg"); d.rect(BD0, TOP_T, BD1, H, "leg")
    pw = PANEL_OPEN_W
    d.rect(FD1, TOP_T, BD0, P_TOP, "wood")                               # top side rail
    d.rect(FD1, P_TOP, FD1 + pw, OPEN_BOT, "face")                       # panel 1
    d.rect(FD1 + pw, P_TOP, FD1 + pw + MUNTIN, OPEN_BOT, "wood")         # centre muntin
    d.rect(FD1 + pw + MUNTIN, P_TOP, BD0, OPEN_BOT, "face")              # panel 2
    d.add(f'<path class="wood" d="{arch_path(d, FD1, BD0, OPEN_BOT, APRON_END, APRON_MID)}"/>')
    # panel edges inside their grooves (hidden)
    e = (PANEL_W - pw) / 2
    for x0 in (FD1, FD1 + pw + MUNTIN):
        d.rect(x0 - e, P_TOP - e, x0 + pw + e, OPEN_BOT + e, "hid")
    d.text(d.x((FD1 + BD0) / 2), d.y(TOP_T + TOP_RAIL / 2) + 2, "top side rail", "n")
    for x0 in (FD1, FD1 + pw + MUNTIN):
        d.dim_h(x0, x0 + pw, d.y(5.0), frac(pw))
        d.text(d.x(x0 + pw / 2), d.y(10.5), "panel", "n")
        d.text(d.x(x0 + pw / 2), d.y(10.5) + 14, f"{frac(PANEL_W)} × {frac(PANEL_H)}", "n")
        d.text(d.x(x0 + pw / 2), d.y(10.5) + 28, "cut size", "n")
    mx = d.x(FD1 + pw + MUNTIN) + 5
    d.text(mx, d.y(16), f"◀ muntin {frac(MUNTIN)}", "n", "start")
    d.text(mx + 10, d.y(16) + 14, f"× {frac(PANEL_OPEN_H)}", "n", "start")
    d.text(d.x((FD1 + BD0) / 2), d.y(OPEN_BOT + 1.0) + 4, "arched bottom rail", "n")
    _floor(d, -1, D + 1)
    d.text(d.x(0.4), d.y(H) - 8, "front", "n", "start")
    d.dim_h(0, D, 42, f"{frac(D)} overall", pyo=d.y(0))
    d.dim_h(0, OV_FB, 68, frac(OV_FB), pyo=d.y(0))
    d.dim_h(OV_FB, D - OV_FB, 68, f"{frac(CASE_D)} case", pyo=d.y(TOP_T))
    d.dim_h(D - OV_FB, D, 68, frac(OV_FB), pyo=d.y(0))
    d.dim_v(0, H, 52, f"{frac(H)} overall", pxo=d.x(0))
    # right: height chain through the side frame, then leg length
    c1 = d.x(D) + 22
    d.dim_v_text(0, TOP_T, c1, frac(TOP_T), pxo=d.x(D))
    d.dim_v_text(TOP_T, P_TOP, c1, frac(TOP_RAIL), pxo=d.x(BD0))
    d.dim_v(P_TOP, OPEN_BOT, c1, f"{frac(PANEL_OPEN_H)} between rails", pxo=d.x(BD0), left=False)
    d.dim_v(OPEN_BOT, OPEN_BOT + APRON_END, c1, frac(APRON_END), pxo=d.x(BD0), left=False)
    d.dim_v(OPEN_BOT + APRON_END, H, c1, frac(H - OPEN_BOT - APRON_END), pxo=d.x(BD0), left=False)
    d.dim_v(TOP_T, H, c1 + 54, f"{frac(LEG_L)} leg", pxo=d.x(BD1), left=False)
    yb = d.y(H) + 28
    d.dim_h(FD0, FD1, yb, frac(LEG), pyo=d.y(H), below=True)
    d.dim_h(FD1, BD0, yb, f"{frac(SIDE_SPAN)} between legs", pyo=d.y(H), below=True)
    d.dim_h(BD0, BD1, yb, frac(LEG), pyo=d.y(H), below=True)
    d.text(d.x(0), yb + 40,
           f"Dashed = panel edges inside their {frac(GROOVE)} grooves ({frac(PLAY)} total play in each direction).", "n", "start")
    d.save(path, "Heartwood Shaker nightstand, side elevation")


def plan(path):
    oy = 100
    d = Drawing(700, 510, 95, oy, s=K)
    Y = lambda dep: oy + (D - dep) * K
    X = d.x

    def prect(x1, a, x2, b, cls):
        d.add(f'<rect class="{cls}" x="{X(x1):.2f}" y="{Y(b):.2f}" width="{(x2-x1)*K:.2f}" height="{(b-a)*K:.2f}"/>')

    def dim_depth(a, b, px, label, pxo=None, left=False):
        ya, yb2 = Y(a), Y(b)
        if pxo is not None:
            for yy in (ya, yb2):
                d.add(f'<line class="ext" x1="{px:.1f}" y1="{yy:.1f}" x2="{pxo:.1f}" y2="{yy:.1f}"/>')
        d.add(f'<line class="dim" x1="{px:.1f}" y1="{ya:.1f}" x2="{px:.1f}" y2="{yb2:.1f}" marker-start="url(#a)" marker-end="url(#a)"/>')
        tx = px - 6 if left else px + 14
        d.add(f'<text class="t" transform="translate({tx:.1f},{(ya+yb2)/2:.1f}) rotate(-90)" text-anchor="middle">{label}</text>')

    d.text(20, 24, "Plan view, top removed — 1 in = 16 px", "h", "start")
    d.add(f'<rect class="hid" x="{X(0):.1f}" y="{Y(D):.1f}" width="{W*K}" height="{D*K}"/>')
    # side frames (flush outside), back rail, front rail
    prect(LX0, FD1, LX0 + FRAME_T, BD0, "wood"); prect(RX1 - FRAME_T, FD1, RX1, BD0, "wood")
    prect(LX1, BD1 - FRAME_T, RX0, BD1, "wood")
    prect(LX1, FD0, RX0, FD0 + FRAME_T, "wood")
    # slide spacers on the side frames, between the legs
    prect(LX0 + FRAME_T, FD1, LX1, FD1 + SPACER_L, "spacer")
    prect(RX0, FD1, RX1 - FRAME_T, FD1 + SPACER_L, "spacer")
    # drawer: front + dashed box
    cx = W / 2
    bx0, bx1 = cx - BOX_W / 2, cx + BOX_W / 2
    by0, by1 = FD0 + FRONT_T, FD0 + FRONT_T + BOX_L
    prect(LX1 + REV, FD0, RX0 - REV, FD0 + FRONT_T, "face")
    d.add(f'<rect class="hid" x="{X(bx0):.1f}" y="{Y(by1):.1f}" width="{BOX_W*K:.1f}" height="{BOX_L*K:.1f}"/>')
    d.text(X(cx), Y(8.5), "drawer box (dashed)", "n")
    d.text(X(cx), Y(8.5) + 14, "3 stacked, each on", "n")
    d.text(X(cx), Y(8.5) + 28, "side-mount slides", "n")
    for x in (LX0, RX0):
        prect(x, FD0, x + LEG, FD1, "leg"); prect(x, BD0, x + LEG, BD1, "leg")
    # box dims, inside the box
    d.dim_h(bx0, bx1, Y(by1 - 1.0), f"{frac(BOX_W)} drawer box")
    dim_depth(by0, by1, X(bx1) - 16, f"{frac(BOX_L)} drawer box", left=True)
    d.dim_h_small(LX1, bx0, Y(4.0), f"{frac(SLIDE_CLR)} slide clearance", side="right")
    # top: overall and overhangs
    d.dim_h(0, W, 42, f"{frac(W)} overall", pyo=Y(D))
    d.dim_h(0, OV_END, 68, frac(OV_END), pyo=Y(D))
    d.dim_h(OV_END, W - OV_END, 68, f"{frac(CASE_W)} case", pyo=Y(BD1))
    d.dim_h(W - OV_END, W, 68, frac(OV_END), pyo=Y(D))
    # below the front: legs and opening
    yb = Y(0) + 28
    d.dim_h(LX0, LX1, yb, frac(LEG), pyo=Y(FD0), below=True)
    d.dim_h(LX1, RX0, yb, f"{frac(OPEN_W)} opening", pyo=Y(FD0), below=True)
    d.dim_h(RX0, RX1, yb, frac(LEG), pyo=Y(FD0), below=True)
    # depth dims
    dim_depth(0, D, X(W) + 24, f"{frac(D)} overall", pxo=X(W))
    dim_depth(OV_FB, D - OV_FB, X(W) + 54, f"{frac(CASE_D)} case", pxo=X(RX1))
    dim_depth(FD1, BD0, X(0) - 22, f"{frac(SIDE_SPAN)} between legs", pxo=X(LX0), left=True)
    d.text(X(cx), yb + 34, "FRONT", "n")
    d.text(X(0), yb + 58, f"Dashed outline = top, {frac(W)} × {frac(D)} × {frac(TOP_T)}, floating on buttons.", "n", "start")
    d.text(X(0), yb + 74, f"Side frames {frac(FRAME_T)} thick, flush to the leg outer faces; grey = "
           f"{frac(SPACER_T)} × {frac(SPACER_W)} × {frac(SPACER_L)} slide spacers.", "n", "start")
    d.save(path, "Heartwood Shaker nightstand, plan view")


def legs(path):
    """Inside faces of the legs: where each rail lands, measured from the top end."""
    oy = 130
    d = Drawing(760, 700, 0, oy, s=K)
    d.text(20, 24, "Leg layout — inside faces, 1 in = 16 px", "h", "start")
    lo = lambda y: y - TOP_T                       # elevation height -> distance from leg top
    arch = (lo(OPEN_BOT), lo(OPEN_BOT + APRON_END))
    top = (0.0, TOP_RAIL)
    faces = [
        ("Front legs — apron face", "(faces the other front leg)",
         [("front rail", lo(r1), lo(r1 + RAIL)), ("front rail", lo(r2), lo(r2 + RAIL)),
          ("front apron", *arch)], None),
        ("Front legs — side face", "(faces the back leg)",
         [("top side rail", *top), ("bottom side rail", *arch)], ("side-panel groove", GROOVE)),
        ("Back legs — side face", "(faces the front leg)",
         [("top side rail", *top), ("bottom side rail", *arch)], ("side-panel groove", GROOVE)),
        ("Back legs — back face", "(faces the other back leg)",
         [("back top rail", *top), ("back bottom rail", *arch)], ("back-panel groove", BACK_GROOVE)),
    ]
    rng = lambda a, b: f"{frac(a) if a else '0'}–{frac(b)}"
    for i, (head, sub, bands, groove) in enumerate(faces):
        d.ox = 120 + i * 170
        fx, fr = d.x(0), d.x(LEG)
        d.text((fx + fr) / 2, oy - 62, head, "sub")
        d.text((fx + fr) / 2, oy - 46, sub, "n")
        d.text(fx - 3, oy - 8, "outside", "n", "end")
        d.text(fr + 3, oy - 8, "inside", "n", "start")
        d.rect(0, 0, LEG, LEG_L, "leg")
        for name, a, b in bands:
            d.rect(0, a, FRAME_T, b, "face")
            m = d.y((a + b) / 2)
            d.text(fr + 8, m - 2, name, "n", "start")
            d.text(fr + 8, m + 12, rng(a, b), "t", "start")
        if groove:
            name, depth = groove
            g0, g1 = TOP_RAIL, lo(OPEN_BOT)
            d.line(FRAME_T / 2, g0, FRAME_T / 2, g1, "hid")
            m = d.y((g0 + g1) / 2)
            d.text(fr + 8, m - 9, name, "n", "start")
            d.text(fr + 8, m + 5, f"{frac(depth)} deep", "n", "start")
            d.text(fr + 8, m + 19, rng(g0, g1), "t", "start")
        d.text((fx + fr) / 2, d.y(LEG_L) + 16, "foot", "n")
    d.ox = 120
    d.dim_v(0, LEG_L, d.x(0) - 30, f"{frac(LEG_L)} leg", pxo=d.x(0))
    yn = d.y(LEG_L) + 44
    d.text(20, yn, "Distances are from the top end of the leg (the underside of the top). Shaded = where each rail lands:", "n", "start")
    d.text(20, yn + 16, f"{frac(FRAME_T)} thick, flush to the leg's outside face. Register every mark from the top end and the outside face,", "n", "start")
    d.text(20, yn + 32, "and the same layout serves left- and right-hand legs. Where two rails enter a leg at the same height, miter the", "n", "start")
    d.text(20, yn + 48, f"tenon tips. The {frac(APRON_END)} rails take a {frac(TEN_W)} × {frac(TEN_T)} tenon (est.), centred; dashed = panel groove.", "n", "start")
    d.save(path, "Heartwood Shaker nightstand, leg layout", EXTRA)


def rail_blank(d, top_px, L, head, name):
    d.oy = top_px
    X, Yp = d.x, d.y
    x0, x1 = TENON, L - TENON
    t0 = (APRON_END - TEN_W) / 2
    t1 = t0 + TEN_W
    chord, rise = x1 - x0, APRON_END - APRON_MID
    R = arc_radius(chord, rise)
    d.text(20, top_px - 78, head, "sub", "start")
    # the square blank before the arch and tenon cheeks are cut
    d.rect(0, 0, x0, APRON_END, "hid"); d.rect(x1, 0, L, APRON_END, "hid")
    d.line(x0, APRON_END, x1, APRON_END, "hid")
    Rp = R * P
    pth = (f'M{X(0):.1f},{Yp(t0):.1f} L{X(x0):.1f},{Yp(t0):.1f} L{X(x0):.1f},{Yp(0):.1f} '
           f'L{X(x1):.1f},{Yp(0):.1f} L{X(x1):.1f},{Yp(t0):.1f} L{X(L):.1f},{Yp(t0):.1f} '
           f'L{X(L):.1f},{Yp(t1):.1f} L{X(x1):.1f},{Yp(t1):.1f} L{X(x1):.1f},{Yp(APRON_END):.1f} '
           f'A{Rp:.1f},{Rp:.1f} 0 0 0 {X(x0):.1f},{Yp(APRON_END):.1f} '
           f'L{X(x0):.1f},{Yp(t1):.1f} L{X(0):.1f},{Yp(t1):.1f} Z')
    d.add(f'<path class="face" d="{pth}"/>')
    d.text(X((x0 + L / 2) / 2), Yp(0.8), name, "n")
    d.dim_h(0, L, top_px - 54, f"{frac(L)} cut length", pyo=Yp(t0))
    d.dim_h(x0, x1, top_px - 28, f"{frac(chord)} shoulder to shoulder", pyo=Yp(0))
    d.dim_v(0, APRON_END, X(0) - 24, frac(APRON_END), pxo=X(x0))
    d.dim_v_text(t0, t1, X(L) + 16, f"{frac(TEN_W)} tenon (est.)", pxo=X(L))
    d.dim_h_small(0, x0, Yp(APRON_END) + 22, f"{frac(TENON)} tenon", pyo=Yp(t1), side="left")
    d.dim_v_text(0, APRON_MID, X(L / 2), f"{frac(APRON_MID)} at centre")
    d.dim_v_text(APRON_MID, APRON_END, X(L / 2), f"{frac(rise)} rise")
    d.text(X(0), Yp(APRON_END) + 50,
           f"Arc: {frac(rise)} rise over the {frac(chord)} between shoulders → radius {r_label(R)}.", "n", "start")


def apron(path):
    d = Drawing(680, 560, 80, 130, s=P)
    d.text(20, 24, "Arched rail blanks — 1 in = 24 px", "h", "start")
    rail_blank(d, 130, OPEN_W + 2 * TENON, "Front apron — 1 required", f"front apron, {frac(FRAME_T)} cherry")
    rail_blank(d, 370, SIDE_SPAN + 2 * TENON, "Bottom side rails — 2 required", f"bottom side rail, {frac(FRAME_T)}")
    yn = d.y(APRON_END) + 82
    d.text(20, yn, "Scribe each arc with a thin batten sprung through the three points, or strike it with a trammel.", "n", "start")
    d.text(20, yn + 16, f"Tenons {frac(TENON)} long × {frac(TEN_W)} wide × {frac(TEN_T)} thick (est.), centred. "
           "Dashed = the square blank before cutting.", "n", "start")
    d.save(path, "Heartwood Shaker nightstand, arched rail blanks", EXTRA)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "..", "static", "static", "woodworking")
    os.makedirs(out, exist_ok=True)
    front(os.path.join(out, "nightstand-front.svg"))
    side(os.path.join(out, "nightstand-side.svg"))
    plan(os.path.join(out, "nightstand-plan.svg"))
    legs(os.path.join(out, "nightstand-legs.svg"))
    apron(os.path.join(out, "nightstand-apron.svg"))
    print("wrote 5 SVGs to", os.path.normpath(out))
