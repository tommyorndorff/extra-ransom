#!/usr/bin/env python3
"""True-scale SVGs for the jeweler's traveling tool chest plan.

Usage: python3 tools/woodworking/jewelers_chest_drawings.py
Writes static/static/woodworking/jewelers-chest-{front,section,side,tray,drawers}.svg
Geometry in inches (heights measured up from the floor, then flipped for the SVG).
Labels are built from the constants with frac(), so edit the constants and re-run.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from modern_craftsman_drawings import Drawing, frac

K = 24                      # px per inch
W, D = 22.0, 12.0           # overall footprint (derived: design choice)
WALL = 0.5                  # case sides, back, well front
BOT_T, SHELF_T = 0.75, 0.75
BAY = 7.0                   # drawer bay, floor of opening to underside of shelf
RAIL = 0.5                  # full-depth rail between the two drawers
DR_OPEN = (BAY - RAIL) / 2  # 3 1/4
REVEAL = 1 / 16
DR_H = DR_OPEN - 2 * REVEAL # 3 1/8 (1/16 reveal top and bottom)
DR_FRONT_T = 0.75
DR_SIDE_T = 0.375
DR_SIDE_H = 3.0
DR_BACK_T = 0.375
DR_BOT_T = 0.25
DR_BOX_D = 10.75            # front face to back of drawer box
CASE_H = 13.0
LID_T = 0.75
LID_FRAME = 2.0             # lid frame member width
LID_PANEL_T = 0.25
PANEL_IN_GROOVE = 3 / 16    # panel edge engagement in the frame groove
TOTAL_H = CASE_H + LID_T    # 13 3/4
SHELF_TOP = BOT_T + BAY + SHELF_T                 # 8 1/2
WELL_FRONT_H = CASE_H - SHELF_TOP                 # 4 1/2
RAIL_LO = BOT_T + DR_OPEN                         # 4
INNER_W = W - 2 * WALL      # 21, between the sides
BOARD_D = D - WALL          # 11 1/2: bottom, shelf and rail, front edge to back board
BACK_H = CASE_H             # back runs floor to lid
CLEAT = 0.5
CLEAT_TOP = 10.75
TRAY_H = 1.75
TRAY_W, TRAY_D = 20.75, 10.75
TRAY_SIDE, TRAY_BOT, TRAY_DIV = 0.375, 0.25, 0.25
TRAY_LIP_DROP = 0.5
TRAY_DIVS = (5.0, 11.0, 15.75)        # divider centres, from the tray's left end
DR_FRONT_W = INNER_W - 2 * REVEAL     # 20 7/8
DR_IN_W = DR_FRONT_W - 2 * DR_SIDE_T  # 20 1/8
DR_IN_D = DR_BOX_D - DR_FRONT_T - DR_BACK_T   # 9 5/8
DR_SIDE_L = DR_BOX_D - DR_FRONT_T     # 10 (sides butt the back of the front)
DR_DIV = 0.25
TOP_BAYS = (6.0, 6.0, 7.625)          # clear compartment widths, soldering drawer
BOT_BAYS = (3.75, 4.75, 4.375, 6.5)   # lapidary drawer; laps bay takes a 6" disc in a sleeve
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "static", "static", "woodworking")

assert abs(sum(TOP_BAYS) + DR_DIV * (len(TOP_BAYS) - 1) - DR_IN_W) < 1e-9
assert abs(sum(BOT_BAYS) + DR_DIV * (len(BOT_BAYS) - 1) - DR_IN_W) < 1e-9

EXTRA = """
<defs>
  <pattern id="jh" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="6" stroke="#8a6a4a" stroke-width="1"/>
  </pattern>
</defs>
<style>
  .cut{fill:#d9b27c;stroke:#4a3320;stroke-width:1.2}
  .beyond{fill:#f8f1e6;stroke:#a08f7c;stroke-width:1}
  .groove{fill:#e6d6bf;stroke:#7a6a5a;stroke-width:1;stroke-dasharray:4 2}
  .dt{fill:url(#jh);stroke:#4a3320;stroke-width:1}
</style>
"""

SUP = {1: "¹⁄₁₆", 3: "³⁄₁₆", 5: "⁵⁄₁₆", 7: "⁷⁄₁₆", 9: "⁹⁄₁₆", 11: "¹¹⁄₁₆", 13: "¹³⁄₁₆", 15: "¹⁵⁄₁₆"}


def fr(v):
    """frac() with the page's typography for sixteenths (³⁄₁₆ rather than 3/16)."""
    s = frac(v)
    for n, g in SUP.items():
        s = s.replace(f"{n}/16", g)
    return s


def fy(h):                  # height above floor -> drawing y (inches, down)
    return TOTAL_H - h


class JD(Drawing):
    """Local helpers on top of the shared Drawing (the shared one stays frozen)."""

    def ext(self, px1, py1, px2, py2):
        self.add(f'<line class="ext" x1="{px1:.1f}" y1="{py1:.1f}" x2="{px2:.1f}" y2="{py2:.1f}"/>')

    def vdim(self, y1, y2, px, label, pxo1=None, pxo2=None, mode="rot"):
        """Vertical dim with each extension line run to its own feature (pixels).
        mode: 'rot' rotated label right of the line, 'rotl' rotated left,
        'txt' upright label right, 'txtl' upright label left."""
        for yy, po in ((y1, pxo1), (y2, pxo2)):
            if po is not None:
                self.ext(px, self.y(yy), po, self.y(yy))
        if mode == "rot":
            self.dim_v(y1, y2, px, label, left=False)
        elif mode == "rotl":
            self.dim_v(y1, y2, px, label, left=True)
        else:
            self.dim_v_text(y1, y2, px, label, side="right" if mode == "txt" else "left")

    def hdim(self, x1, x2, py, label, pyo1=None, pyo2=None, below=True):
        for xx, po in ((x1, pyo1), (x2, pyo2)):
            if po is not None:
                self.ext(self.x(xx), py, self.x(xx), po)
        self.dim_h(x1, x2, py, label, below=below)

    def tail(self, x1, x2, py, label, pyo1=None, pyo2=None, side="right"):
        """Short span at the end of a chain: plain line across the span, one arrow
        outside the free end pointing in, label beyond it."""
        a, b = self.x(x1), self.x(x2)
        for xx, po in ((a, pyo1), (b, pyo2)):
            if po is not None:
                self.ext(xx, py, xx, po)
        self.add(f'<line class="dim" x1="{a:.1f}" y1="{py:.1f}" x2="{b:.1f}" y2="{py:.1f}"/>')
        if side == "right":
            self.add(f'<line class="dim" x1="{b+14:.1f}" y1="{py:.1f}" x2="{b:.1f}" y2="{py:.1f}" marker-end="url(#a)"/>')
            self.text(b + 18, py + 4, label, "t", "start")
        else:
            self.add(f'<line class="dim" x1="{a-14:.1f}" y1="{py:.1f}" x2="{a:.1f}" y2="{py:.1f}" marker-end="url(#a)"/>')
            self.text(a - 18, py + 4, label, "t", "end")

    def block(self, cx, cy, title, lines, step=14):
        """Centred title (class t) and note lines (class n), all in pixels."""
        top = cy - step * len(lines) / 2
        self.text(cx, top, title, "t")
        for i, s in enumerate(lines):
            self.text(cx, top + step * (i + 1) + 2, s, "n")


def front():
    d = JD(780, 520, 110, 95, s=K)
    d.text(20, 24, "Front elevation — 1 in = 24 px", "h", "start")
    d.rect(0, fy(TOTAL_H), W, fy(CASE_H), "wood")                       # lid
    d.rect(0, fy(CASE_H), WALL, fy(0), "leg")                           # sides
    d.rect(W - WALL, fy(CASE_H), W, fy(0), "leg")
    d.rect(WALL, fy(CASE_H), W - WALL, fy(SHELF_TOP), "face")           # well front
    d.rect(WALL, fy(SHELF_TOP), W - WALL, fy(SHELF_TOP - SHELF_T), "wood")   # shelf edge
    d.rect(WALL, fy(RAIL_LO + RAIL), W - WALL, fy(RAIL_LO), "wood")     # rail edge
    d.rect(WALL, fy(BOT_T), W - WALL, fy(0), "wood")                    # bottom edge
    x1, x2 = WALL + REVEAL, W - WALL - REVEAL
    los = (BOT_T + REVEAL, RAIL_LO + RAIL + REVEAL)
    for lo in los:
        d.rect(x1, fy(lo + DR_H), x2, fy(lo), "face")
        cx, cy = (x1 + x2) / 2, fy(lo + DR_H / 2)
        d.add(f'<circle class="pull" cx="{d.x(cx):.1f}" cy="{d.y(cy):.1f}" r="{0.3*K:.1f}"/>')
        d.add(f'<circle cx="{d.x(cx):.1f}" cy="{d.y(cy):.1f}" r="{0.15*K:.1f}" fill="#fff"/>')
    # drawer-front size dimensioned inside the upper front (arrows on its own edges)
    py = d.y(fy(los[1] + DR_H)) + 20
    d.dim_h(x1, x2, py, f"drawer fronts {fr(DR_FRONT_W)} × {fr(DR_H)} ({fr(REVEAL)} reveals)")
    # lock escutcheon on the well front
    lx, ly = W / 2, fy(CASE_H - 0.9)
    d.rect(lx - 0.45, ly - 0.5, lx + 0.45, ly + 0.5, "pull")
    d.text(d.x(lx), d.y(ly) + 38, "half-mortise lid lock", "n")
    d.add(f'<line class="floor" x1="{d.x(-3):.1f}" y1="{d.y(fy(0)):.1f}" x2="{d.x(W+3):.1f}" y2="{d.y(fy(0)):.1f}"/>')
    # dimensions
    xl, xr = d.x(0), d.x(W)
    d.dim_h(0, W, 55, f"{fr(W)} overall", pyo=d.y(0))
    d.vdim(fy(TOTAL_H), fy(0), xl - 62, f"{fr(TOTAL_H)} overall", xl, xl, "rotl")
    d.vdim(fy(SHELF_TOP - SHELF_T), fy(BOT_T), xl - 32, f"{fr(BAY)} drawer bay", xl, xl, "rotl")
    R = xr + 30
    chain = [
        (TOTAL_H, CASE_H, f"{fr(LID_T)} lid", "txt"),
        (CASE_H, SHELF_TOP, f"{fr(WELL_FRONT_H)} well front", "rot"),
        (SHELF_TOP, SHELF_TOP - SHELF_T, f"{fr(SHELF_T)} shelf", "txt"),
        (SHELF_TOP - SHELF_T, RAIL_LO + RAIL, f"{fr(DR_OPEN)} opening", "rot"),
        (RAIL_LO + RAIL, RAIL_LO, f"{fr(RAIL)} rail", "txt"),
        (RAIL_LO, BOT_T, f"{fr(DR_OPEN)} opening", "rot"),
        (BOT_T, 0, f"{fr(BOT_T)} bottom", "txt"),
    ]
    for top, bot, lab, mode in chain:
        d.vdim(fy(top), fy(bot), R, lab, xr, xr, mode)
    yf = d.y(fy(0))
    d.hdim(WALL, W - WALL, yf + 28, f"{fr(INNER_W)} between the {fr(WALL)} sides", yf, yf)
    # bail handles last, so the extension lines run to them rather than through them
    d.rect(-0.55, fy(8.7), 0, fy(7.0), "pull")
    d.rect(W, fy(8.7), W + 0.55, fy(7.0), "pull")
    d.text(20, 500, "Bail handle on each end (dark blocks). Heights are above the floor; the lid is flush with the case front and back.", "n", "start")
    d.save(os.path.join(OUT, "jewelers-chest-front.svg"), "Jeweler's traveling chest, front elevation", EXTRA)


def section():
    d = JD(780, 590, 120, 110, s=K)
    d.text(20, 24, "Cross-section at centre, looking toward the left end — 1 in = 24 px", "h", "start")
    # beyond the cut: inside face of the left side
    d.rect(0, fy(CASE_H), BOARD_D, fy(0), "beyond")
    # lid: front and back frame members and the panel are cut; the left end member is beyond
    d.rect(LID_FRAME, fy(TOTAL_H), D - LID_FRAME, fy(CASE_H), "beyond")
    d.rect(0, fy(TOTAL_H), LID_FRAME, fy(CASE_H), "cut")
    d.rect(D - LID_FRAME, fy(TOTAL_H), D, fy(CASE_H), "cut")
    pm = CASE_H + LID_T / 2
    d.rect(LID_FRAME - PANEL_IN_GROOVE, fy(pm + LID_PANEL_T / 2), D - LID_FRAME + PANEL_IN_GROOVE,
           fy(pm - LID_PANEL_T / 2), "cut")
    # case: well front, back, bottom, rail, shelf, cleats
    d.rect(0, fy(CASE_H), WALL, fy(SHELF_TOP), "cut")
    d.rect(BOARD_D, fy(BACK_H), D, fy(0), "cut")
    d.rect(0, fy(BOT_T), BOARD_D, fy(0), "cut")
    d.rect(0, fy(RAIL_LO + RAIL), BOARD_D, fy(RAIL_LO), "cut")
    d.rect(0, fy(SHELF_TOP), BOARD_D, fy(SHELF_TOP - SHELF_T), "cut")
    d.rect(WALL, fy(CLEAT_TOP), WALL + CLEAT, fy(CLEAT_TOP - CLEAT), "spacer")
    d.rect(BOARD_D - CLEAT, fy(CLEAT_TOP), BOARD_D, fy(CLEAT_TOP - CLEAT), "spacer")
    # tray: left end beyond (full height), front lip / back / bottom cut
    t0 = WALL + (D - 2 * WALL - TRAY_D) / 2
    t1 = t0 + TRAY_D
    d.rect(t0, fy(CLEAT_TOP + TRAY_H), t1, fy(CLEAT_TOP), "beyond")
    d.rect(t0, fy(CLEAT_TOP + TRAY_H - TRAY_LIP_DROP), t0 + TRAY_SIDE, fy(CLEAT_TOP), "cut")
    d.rect(t1 - TRAY_SIDE, fy(CLEAT_TOP + TRAY_H), t1, fy(CLEAT_TOP), "cut")
    d.rect(t0 + TRAY_SIDE, fy(CLEAT_TOP + TRAY_BOT), t1 - TRAY_SIDE, fy(CLEAT_TOP), "cut")
    tm = d.y(fy(CLEAT_TOP + TRAY_H))
    d.text(d.x(D / 2 - 0.2), tm + 17, f"lift-out tray, {fr(TRAY_H)} deep", "n")
    d.text(d.x(D / 2 - 0.2), tm + 31, f"front lip cut {fr(TRAY_LIP_DROP)} lower", "n")
    # drawers: sides ride on the bottom / rail; fronts sit a reveal above
    for floor_h, name in ((RAIL_LO + RAIL, "top drawer — soldering kit"), (BOT_T, "bottom drawer — lapidary kit")):
        d.rect(DR_FRONT_T, fy(floor_h + DR_SIDE_H), DR_BOX_D, fy(floor_h), "beyond")
        d.rect(0, fy(floor_h + REVEAL + DR_H), DR_FRONT_T, fy(floor_h + REVEAL), "cut")
        d.rect(DR_FRONT_T, fy(floor_h + DR_BOT_T), DR_BOX_D - DR_BACK_T, fy(floor_h), "cut")
        d.rect(DR_BOX_D - DR_BACK_T, fy(floor_h + DR_SIDE_H), DR_BOX_D, fy(floor_h + DR_BOT_T), "cut")
        d.text(d.x((DR_FRONT_T + DR_BOX_D) / 2), d.y(fy(floor_h + DR_SIDE_H / 2)) + 4, name, "n")
    # hinge
    d.rect(D - 0.1, fy(CASE_H + 0.1), D + 0.2, fy(CASE_H - 0.5), "pull")
    d.leader(d.x(D + 0.2), d.y(fy(CASE_H + 0.1)), d.x(D) + 46, 96, "butt hinge (×2)")
    d.add(f'<line class="floor" x1="{d.x(-3):.1f}" y1="{d.y(fy(0)):.1f}" x2="{d.x(D+4):.1f}" y2="{d.y(fy(0)):.1f}"/>')
    # dims — top
    d.dim_h(0, D, 72, f"{fr(D)} deep", pyo=d.y(fy(TOTAL_H)))
    d.text(d.x(D / 2), 100, f"lid: {fr(LID_FRAME)} frame, {fr(LID_PANEL_T)} floating panel", "n")
    # left
    xl = d.x(0)
    d.vdim(fy(CASE_H), fy(0), xl - 62, f"{fr(CASE_H)} case (back runs full height)", xl, xl, "rotl")
    d.vdim(fy(CLEAT_TOP), fy(0), xl - 30, f"{fr(CLEAT_TOP)} floor to top of cleats", d.x(WALL), xl, "rotl")
    d.vdim(fy(TOTAL_H), fy(CASE_H), xl - 30, f"{fr(LID_T)} lid", xl, xl, "txtl")
    # right: the well
    R = d.x(D) + 30
    d.vdim(fy(CLEAT_TOP), fy(SHELF_TOP), R, f"{fr(CLEAT_TOP - SHELF_TOP)} under tray", d.x(BOARD_D), d.x(BOARD_D), "txt")
    d.vdim(fy(CLEAT_TOP + TRAY_H), fy(CLEAT_TOP), R, f"{fr(TRAY_H)} tray", d.x(t1), None, "txt")
    d.vdim(fy(CASE_H), fy(CLEAT_TOP + TRAY_H), R, f"{fr(CASE_H - CLEAT_TOP - TRAY_H)} clear", d.x(D), None, "txt")
    # tray width inside the well, under the tray
    yb = d.y(fy(CLEAT_TOP))
    clear = (D - 2 * WALL - TRAY_D) / 2
    d.hdim(t0, t1, yb + 22, f"tray {fr(TRAY_D)}, {fr(clear)} clear each end", yb, yb, below=False)
    d.text(d.x(D / 2), d.y(fy(SHELF_TOP)) - 8, "well: hammers, mandrel, saw frame, torch tips", "n")
    # bottom rows
    yf = d.y(fy(0))
    yd = d.y(fy(BOT_T))
    d.hdim(0, DR_BOX_D, yf + 26, f"drawer box {fr(DR_BOX_D)}", yd, yd)
    d.tail(DR_BOX_D, BOARD_D, yf + 26, f"{fr(BOARD_D - DR_BOX_D)} stop gap", None, yd)
    d.hdim(0, BOARD_D, yf + 54, f"bottom, rail, shelf {fr(BOARD_D)}", yf, yf)
    d.tail(BOARD_D, D, yf + 54, f"{fr(WALL)} back", None, yf)
    d.text(20, 548, "Solid = cut at the centre line; light = seen beyond it (left side, drawer sides, tray end). "
                    "The top drawer runs on the full-depth rail.", "n", "start")
    d.text(20, 566, f"Drawer sides {fr(DR_SIDE_T)} maple, {fr(DR_BOT_T)} bottoms, {fr(DR_FRONT_T)} fronts; "
                    f"the {fr(BOARD_D - DR_BOX_D)} gap behind the drawers is a dust/stop space.", "n", "start")
    d.save(os.path.join(OUT, "jewelers-chest-section.svg"), "Jeweler's traveling chest, cross-section", EXTRA)


def side():
    d = JD(780, 480, 130, 90, s=K)
    fs = lambda h: CASE_H - h
    d.text(20, 24, "Left side, inside face: joint layout — 1 in = 24 px", "h", "start")
    d.rect(0, fs(CASE_H), D, fs(0), "face")
    d.rect(BOARD_D, fs(CASE_H), D, fs(0), "groove")                                  # back rabbet
    bands = [
        (0, BOT_T, f"groove for the {fr(BOT_T)} bottom: floor to {fr(BOT_T)}"),
        (RAIL_LO, RAIL_LO + RAIL, f"groove for the {fr(RAIL)} rail: {fr(RAIL_LO)} to {fr(RAIL_LO + RAIL)}"),
        (SHELF_TOP - SHELF_T, SHELF_TOP, f"shelf through-mortises: {fr(SHELF_TOP - SHELF_T)} to {fr(SHELF_TOP)}"),
    ]
    for lo, hi, lab in bands:
        d.rect(0, fs(hi), BOARD_D, fs(lo), "groove")
        ym = d.y(fs((lo + hi) / 2))
        d.leader(d.x(BOARD_D), ym, d.x(D) + 24, ym, lab, cls="t")
    d.rect(0, fs(CASE_H), WALL, fs(SHELF_TOP), "dt")                                 # well-front dovetails
    ym = d.y(fs(CLEAT_TOP + 0.6))
    d.leader(d.x(WALL), ym, d.x(D) + 24, ym, f"dovetails to the {fr(WALL)} well front: {fr(SHELF_TOP)} to {fr(CASE_H)}", cls="t")
    d.text(d.x(BOARD_D / 2), d.y(fs((BOT_T + RAIL_LO) / 2)) + 4, "drawer bay", "n")
    d.text(d.x(BOARD_D / 2), d.y(fs((RAIL_LO + RAIL + SHELF_TOP - SHELF_T) / 2)) + 4, "drawer bay", "n")
    d.text(d.x(BOARD_D / 2), d.y(fs((SHELF_TOP + CASE_H) / 2)) + 4, "well", "n")
    # dims
    d.dim_h(0, D, 46, f"{fr(D)}", pyo=d.y(0))
    d.dim_h_small(BOARD_D, D, 74, f"{fr(WALL)} rabbet for the back", pyo=d.y(0))
    xl = d.x(0)
    d.vdim(fs(CASE_H), fs(0), xl - 62, f"{fr(CASE_H)}", xl, xl, "rotl")
    d.vdim(fs(CASE_H), fs(SHELF_TOP), xl - 30, f"{fr(WELL_FRONT_H)}", xl, xl, "rotl")
    d.text(d.x(0), d.y(fs(0)) + 18, "◀ FRONT edge", "n", "start")
    d.text(d.x(D), d.y(fs(0)) + 18, "BACK edge ▶", "n", "end")
    d.text(20, 446, "Left side seen from inside the chest. The right side is its mirror image: lay it out with the front edge on the right.", "n", "start")
    d.text(20, 462, f"Groove, rabbet and tail depths are your choice: add them to the {fr(INNER_W)} between-the-sides lengths in the cut list.", "n", "start")
    d.save(os.path.join(OUT, "jewelers-chest-side.svg"), "Jeweler's traveling chest, side joint layout", EXTRA)


def tray_bays():
    """Clear compartment spans (x1, x2) between the tray sides and the 1/4" dividers."""
    edges = [TRAY_SIDE]
    for c in TRAY_DIVS:
        edges += [c - TRAY_DIV / 2, c + TRAY_DIV / 2]
    edges.append(TRAY_W - TRAY_SIDE)
    return [(edges[i], edges[i + 1]) for i in range(0, len(edges), 2)]


def tray():
    d = JD(780, 470, 70, 80, s=K)
    iw, idp = TRAY_W - 2 * TRAY_SIDE, TRAY_D - 2 * TRAY_SIDE
    d.text(20, 24, f"Lift-out tray, plan — 1 in = 24 px (inside {fr(iw)} × {fr(idp)})", "h", "start")
    d.rect(0, 0, TRAY_W, TRAY_D, "wood")
    y1, y2 = TRAY_SIDE, TRAY_D - TRAY_SIDE
    bays = tray_bays()
    for c in TRAY_DIVS:
        d.rect(c - TRAY_DIV / 2, y1, c + TRAY_DIV / 2, y2, "wood")
    labels = [
        ("pliers + cutters", ["jaws up in a", "slotted block,", "8–10 tools"]),
        ("files", ["hand + needle files,", "two rows, 6–8″"]),
        ("measuring", ["dividers, calipers,", "rule, ring sizer"]),
    ]
    for (a, b), (t, ls) in zip(bays[:3], labels):
        d.rect(a, y1, b, y2, "face")
        d.block(d.x((a + b) / 2), d.y(TRAY_D / 2), t, ls)
    a, b = bays[3]
    ym = TRAY_D / 2
    d.rect(a, y1, b, ym - TRAY_DIV / 2, "face")
    d.rect(a, ym - TRAY_DIV / 2, b, ym + TRAY_DIV / 2, "wood")
    d.rect(a, ym + TRAY_DIV / 2, b, y2, "face")
    d.block(d.x((a + b) / 2), d.y((y1 + ym) / 2), "", ["burnishers,", "pushers, scribes"])
    d.block(d.x((a + b) / 2), d.y((ym + y2) / 2), "", ["burs in index", "cases, loupes"])
    # dims
    d.dim_h(0, TRAY_W, 50, f"{fr(TRAY_W)} tray", pyo=d.y(0))
    d.vdim(0, TRAY_D, d.x(0) - 30, f"{fr(TRAY_D)}", d.x(0), d.x(0), "rotl")
    yb = d.y(TRAY_D) + 26
    for a, b in bays:
        d.hdim(a, b, yb, fr(b - a), d.y(y2), d.y(y2))
    R = d.x(TRAY_W) + 30
    xin = d.x(TRAY_W - TRAY_SIDE)
    d.vdim(y1, ym - TRAY_DIV / 2, R, fr(ym - TRAY_DIV / 2 - y1), xin, xin, "rot")
    d.vdim(ym + TRAY_DIV / 2, y2, R, fr(y2 - ym - TRAY_DIV / 2), xin, xin, "rot")
    d.text(d.x(TRAY_W / 2), yb + 42, f"FRONT — this side's lip is cut down {fr(TRAY_LIP_DROP)}", "n")
    d.text(20, 450, f"Mitered {fr(TRAY_SIDE)} sides, {fr(TRAY_BOT)} bottom, {fr(TRAY_DIV)} dividers. "
                    "Bottom-row and right-hand numbers are clear compartment sizes.", "n", "start")
    d.save(os.path.join(OUT, "jewelers-chest-tray.svg"), "Jeweler's traveling chest, tray layout", EXTRA)


def drawer_plan(d, top_px, title, bays, items, overall):
    y0 = top_px / K                      # back of the drawer box, in drawing inches
    yi0, yi1 = y0 + DR_BACK_T, y0 + DR_SIDE_L   # inside, back to front
    d.text(20, top_px - (60 if overall else 14), title, "t", "start")
    d.rect(0, y0, DR_SIDE_T, yi1, "wood")
    d.rect(DR_FRONT_W - DR_SIDE_T, y0, DR_FRONT_W, yi1, "wood")
    d.rect(DR_SIDE_T, y0, DR_FRONT_W - DR_SIDE_T, yi0, "wood")
    d.rect(0, yi1, DR_FRONT_W, y0 + DR_BOX_D, "wood")
    d.text(d.x(DR_FRONT_W / 2), d.y(yi1 + DR_FRONT_T / 2) + 4, f"front {fr(DR_FRONT_T)}", "n")
    x = DR_SIDE_T
    spans = []
    for i, w in enumerate(bays):
        d.rect(x, yi0, x + w, yi1, "face")
        spans.append((x, x + w))
        if i < len(bays) - 1:
            d.rect(x + w, yi0, x + w + DR_DIV, yi1, "wood")
        x += w + DR_DIV
    for (a, b), (t, ls) in zip(spans, items):
        d.block(d.x((a + b) / 2), d.y((yi0 + yi1) / 2), t, ls)
    yb = d.y(y0 + DR_BOX_D) + 24
    for a, b in spans:
        d.hdim(a, b, yb, fr(b - a), d.y(yi1), d.y(yi1))
    R = d.x(DR_FRONT_W)
    d.vdim(yi0, yi1, R + 28, f"{fr(DR_IN_D)} inside", R - DR_SIDE_T * K, R - DR_SIDE_T * K, "rot")
    d.vdim(y0, y0 + DR_BOX_D, R + 62, f"{fr(DR_BOX_D)} box", R, R, "rot")
    if overall:
        d.dim_h(0, DR_FRONT_W, top_px - 42, f"{fr(DR_FRONT_W)} front and box", pyo=top_px)
        d.hdim(DR_SIDE_T, DR_FRONT_W - DR_SIDE_T, top_px - 14, f"{fr(DR_IN_W)} inside", None, None, below=False)
        d.ext(d.x(DR_SIDE_T), top_px - 14, d.x(DR_SIDE_T), d.y(yi0))
        d.ext(d.x(DR_FRONT_W - DR_SIDE_T), top_px - 14, d.x(DR_FRONT_W - DR_SIDE_T), d.y(yi0))


def drawer_side_section(d, top_px):
    """Side section of one drawer box at its centre, front at left (as in the case section)."""
    top_h = REVEAL + DR_H
    gy = lambda h: top_px / K + (top_h - h)
    d.rect(DR_FRONT_T, gy(DR_SIDE_H), DR_BOX_D, gy(0), "beyond")
    d.rect(0, gy(REVEAL + DR_H), DR_FRONT_T, gy(REVEAL), "cut")
    d.rect(DR_FRONT_T, gy(DR_BOT_T), DR_BOX_D - DR_BACK_T, gy(0), "cut")
    d.rect(DR_BOX_D - DR_BACK_T, gy(DR_SIDE_H), DR_BOX_D, gy(DR_BOT_T), "cut")
    d.text(d.x(DR_BOX_D / 2 + 0.3), d.y(gy(DR_SIDE_H / 2)) + 4, f"side {fr(DR_SIDE_T)} × {fr(DR_SIDE_H)} × {fr(DR_SIDE_L)} (beyond)", "n")
    xl, xr = d.x(0), d.x(DR_BOX_D)
    d.vdim(gy(REVEAL + DR_H), gy(REVEAL), xl - 24, f"{fr(DR_H)}", xl, xl, "rotl")
    d.vdim(gy(DR_SIDE_H), gy(0), xr + 24, f"{fr(DR_SIDE_H)} side", xr, xr, "rot")
    d.vdim(gy(DR_SIDE_H), gy(DR_BOT_T), xr + 64, f"{fr(DR_SIDE_H - DR_BOT_T)} back / inside", xr, xr, "txt")
    yb = d.y(gy(0))
    yf = d.y(gy(REVEAL))
    d.hdim(DR_FRONT_T, DR_BOX_D, yb + 24, f"{fr(DR_SIDE_L)} side", yb, yb)
    d.tail(0, DR_FRONT_T, yb + 24, f"{fr(DR_FRONT_T)} front", yf, None, side="left")
    d.hdim(DR_FRONT_T, DR_BOX_D - DR_BACK_T, yb + 52, f"{fr(DR_IN_D)} inside", yb, yb)
    d.tail(DR_BOX_D - DR_BACK_T, DR_BOX_D, yb + 52, f"{fr(DR_BACK_T)} back", None, yb)


def drawers():
    d = JD(780, 1030, 90, 0, s=K)
    d.text(20, 24, f"Drawers, plan — 1 in = 24 px (each {fr(DR_IN_W)} × {fr(DR_IN_D)} × "
                   f"{fr(DR_SIDE_H - DR_BOT_T)} inside)", "h", "start")
    top_items = [
        ("solder + flux", ["sheet and wire in", "labeled tubes, flux", "bottle, borax dish"]),
        ("firing tools", ["tweezers, third hand,", "ceramic tile, ring", "clamp, bench-pin", "inserts"]),
        ("finished + in progress", ["lidded boxes for rings,", "pendants and findings", "(no loose pieces)"]),
    ]
    bot_items = [
        ("dops + wax", ["dop sticks on", "edge in a", "slotted rack,", "wax, lamp tin"]),
        ("grit + polish", ["sealed jars, one", "per grit; never", "share a lid or", "sponge"]),
        ("templates", ["cab templates,", "calipers, loupes,", "gem tweezers,", "wrapped stones"]),
        ("laps", ["6″ faceting and flat", "laps in padded", "sleeves, stacked flat"]),
    ]
    drawer_plan(d, 120, "TOP — soldering kit", TOP_BAYS, top_items, True)
    drawer_plan(d, 466, "BOTTOM — lapidary teaching kit", BOT_BAYS, bot_items, False)
    d.text(20, 806, "Drawer box, side section at centre (front at left)", "t", "start")
    drawer_side_section(d, 826)
    d.text(20, 1000, f"Front at the bottom of each plan. Bottom-row numbers are clear compartment widths between "
                     f"{fr(DR_DIV)} removable dividers,", "n", "start")
    d.text(20, 1016, "so each kit can be rearranged for a different workshop. Sides butt the back of the front "
                     "as sized; add your rabbet depth to the side length.", "n", "start")
    d.save(os.path.join(OUT, "jewelers-chest-drawers.svg"), "Jeweler's traveling chest, drawer layouts", EXTRA)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    front(); section(); side(); tray(); drawers()
    print("wrote", os.path.normpath(OUT))
