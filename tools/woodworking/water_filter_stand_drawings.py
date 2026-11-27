#!/usr/bin/env python3
"""Drawings for the gravity water-filter floor stand (BOROUX / Berkey / British Berkefeld
class sized filters).

FOUR VERTICAL LEGS AT THE COMPASS POINTS, joined by TWO CROSS MEMBERS HALF-LAPPED INTO AN "X".
The filter's base ring drops between the four legs and SITS ON THE X; the legs stand above it
as retaining posts. A small shelf is tucked into one corner between two legs, under the spigot.

Usage: python3 tools/woodworking/water_filter_stand_drawings.py
Writes public/static/woodworking/water-stand-*.svg
Geometry is in inches. Plan coordinates: x = left/right, y = back(-)/front(+), z = up
from the floor or counter. Legs "A" lie on the x axis, legs "B" on the y axis. The
spigot faces the shelf corner, azimuth 135 degrees (toward -x, +y). Edit the constants
and re-run; the drawings and the numbers printed at the end come from the same constants.
The tables on the plan page are written by hand, so update them after a re-run.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from modern_craftsman_drawings import Drawing


def frac(v):
    """Inches -> a label such as 13⅜″ or 12 11/16″ (a space keeps sixteenths readable after a whole number)."""
    glyph = {1: "1/16", 2: "⅛", 3: "3/16", 4: "¼", 5: "5/16", 6: "⅜", 7: "7/16", 8: "½",
             9: "9/16", 10: "⅝", 11: "11/16", 12: "¾", 13: "13/16", 14: "⅞", 15: "15/16"}
    whole, rem = divmod(round(v * 16), 16)
    if rem == 0:
        return f"{whole}″"
    g = glyph[rem]
    return (f"{whole}" + (" " if "/" in g else "") if whole else "") + g + "″"

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "public", "static", "woodworking")

# ---- shared construction ---------------------------------------------------
W_TOP = 2.0                    # leg width (in its own plane) at the top, read off the Berkey oak-stand photo
LEG_BLANK_W = 2.25             # blank width the legs are cut from
LEG_T = 1.25                   # leg thickness across that plane
GAP = 9.75                     # between opposite legs' inside faces at the leg tops (9 1/2 base + 1/4)
FOOT_W = 1.125                 # leg width at the foot (about 55% of the top, as in the photo)
# THE LEGS ARE VERTICAL: the outside edge is plumb, top and foot are square. The inside face is plumb from the leg top
# down to the bottom of the X (so the bars butt square and the Dominos register off a flat face), then tapers OUTWARD
# toward the foot, so the leg narrows and the gap between the legs widens toward the floor.
# S_IN is derived after the heights below, so changing GAP, F_H or F_BAR_TOP and re-running just works.
BAR_H, BAR_T = 2.5, 1.0        # cross members: 2 1/2" tall x 1" thick, tops flush at the X
MM = 1 / 25.4
# Festool Domino joinery. Bar ends: two 8x40 Dominos (8 mm thick, about 22 mm wide, 40 mm long: 20 mm into each part)
# stacked up the bar end. Shelf: one 5x30 Domino (15 mm into each part) at each leg.
DOM_T, DOM_W, DOM_DEPTH, DOM_PITCH = 8 * MM, 22 * MM, 20 * MM, 30 * MM
SH_T, SH_W, SH_DEPTH = 5 * MM, 19 * MM, 15 * MM
SHELF_T = 0.75
SHELF_CLR = 0.0                # the shelf is glued to the legs with Dominos, so its edges touch them
NOZ_AZ = 135.0                 # spigot azimuth, deg from +x (toward -x, +y): the shelf corner

# ---- floor stand -------------------------------------------------------------
F_BAR_TOP = 33.75              # X top = where the filter base sits (BOROUX figure)
F_POST = 2.0                   # legs stand this far above the X, as retaining posts (a short post, as in the photo)
F_H = F_BAR_TOP + F_POST       # leg height (vertical)
F_SHELF_TOP = 23.0             # BOROUX figure
SHELF_X0, SHELF_Y1 = -9.0, 9.0            # the shelf fills the corner x in [SHELF_X0, -edge], y in [edge, SHELF_Y1]
SHELF_CHAMF = 2.5

# ---- countertop stand ---------------------------------------------------------
C_BAR_TOP = 8.0
C_H = C_BAR_TOP + F_POST

S_IN = (W_TOP - FOOT_W) / (F_BAR_TOP - BAR_H)           # inside edge below the kink: it moves OUTWARD this much per inch of height

# ---- the filters this is sized for (maker figures, rounded; measure yours) ---
MODELS = [  # name, diameter, height with lid
    ("BOROUX 1.8-Gallon", 9.5, 17.5),   # dia = published base limit; height = 51.25 - 33.75 (BOROUX diagram)
    ("BOROUX 3-Gallon", 9.5, 23.0),     # height = 56.75 - 33.75 (BOROUX diagram); body width not published
    ("Travel Berkey", 7.5, 18.0),
    ("Big Berkey", 8.5, 19.25),
    ("Royal Berkey", 9.5, 23.0),
    ("Imperial Berkey", 10.0, 26.0),
    ("British Berkefeld 8.5 L", 10.25, 19.3),
    ("British Berkefeld 12 L", 9.7, 23.75),
    ("Crown Berkey", 11.0, 30.0),
]
GHOST_D, GHOST_H = 9.5, 23.0    # BOROUX 3-Gallon, drawn dashed (9 1/2" = its published base limit)
SPIGOT_OUT = 2.6                # how far the nozzle sticks out of the body (est.)
SPIGOT_UP = 0.25                # nozzle underside above the filter base: BOROUX lifts the spigot to 34", the base sits at 33 3/4"
CUP_D, CUP_H = 3.3, 7.5         # a 30 oz tumbler (est.)

EXTRA = """
<style>
  .post{fill:#dcb988;stroke:#4a3320;stroke-width:1.3;stroke-linejoin:round}
  .ap{fill:#ecd2ac;stroke:#4a3320;stroke-width:1.3;stroke-linejoin:round}
  .shelfp{fill:#e6c79c;stroke:#4a3320;stroke-width:1.3;stroke-linejoin:round}
  .ghost{fill:#eef1f4;fill-opacity:.55;stroke:#6b7885;stroke-width:1.2;stroke-dasharray:6 4}
  .cup{fill:none;stroke:#b0452b;stroke-width:1.2;stroke-dasharray:3 3}
  .ctr{stroke:#999;stroke-width:.8;stroke-dasharray:10 3 2 3}
  .cut{fill:#fff;stroke:#4a3320;stroke-width:1.3}
</style>
"""


# ---------------------------------------------------------------------------
# geometry
# ---------------------------------------------------------------------------
def bar_top_for(H):
    return F_BAR_TOP if abs(H - F_H) < 1e-9 else C_BAR_TOP


def kink(H):
    """Height where the inside face stops being plumb: the bottom of the X."""
    return bar_top_for(H) - BAR_H


def inner(z, H):
    """Horizontal distance from the stand's axis to a leg's inside face at height z (plumb above the kink)."""
    k = kink(H)
    return GAP / 2 if z >= k else GAP / 2 + S_IN * (k - z)


def outer(z, H):
    """Outside face: plumb (the legs are vertical)."""
    return GAP / 2 + W_TOP


def leg_w(z, H):
    return outer(z, H) - inner(z, H)


def leg_poly(sg, H, dx=0.0, zf=lambda z: z):
    """Leg outline in its own plane, as (x, z) points: square top, inside face plumb to the kink, then tapering outward to a square foot."""
    k = kink(H)
    return [(dx + sg * outer(H, H), zf(H)), (dx + sg * inner(H, H), zf(H)), (dx + sg * inner(k, H), zf(k)),
            (dx + sg * inner(0, H), zf(0)), (dx + sg * outer(0, H), zf(0))]


def nozzle_xy(r=GHOST_D / 2 + SPIGOT_OUT):
    a = math.radians(NOZ_AZ)
    return r * math.cos(a), r * math.sin(a)


def cup_xy():
    return nozzle_xy(GHOST_D / 2 + SPIGOT_OUT - 0.4)


def shelf_edge():
    """Shelf edges sit this far from the axes: against the leg faces, 1/16" clear."""
    return LEG_T / 2 + SHELF_CLR


def shelf_pts():
    e, x0, y1, c = shelf_edge(), SHELF_X0, SHELF_Y1, SHELF_CHAMF
    return [(x0, e), (-e, e), (-e, y1), (x0 + c, y1), (x0, y1 - c)]


def bar_len(bar_top, H):
    return GAP                      # the bar butts square against the plumb inside faces; Dominos do the joining


# ===========================================================================
# Elevations
# ===========================================================================
def elevations(path, floor=True):
    H = F_H if floor else C_H
    BT = F_BAR_TOP if floor else C_BAR_TOP
    S = 10 if floor else 15
    zmax = BT + GHOST_H + 2.0
    W, HGT = 1000, int(zmax * S + 255)
    d = Drawing(W, HGT, 250, 70, s=S)
    zy = lambda z: zmax - z
    name = "Floor stand" if floor else "Countertop stand"
    d.text(20, 26, f"{name} — front and side elevations (1 in = {S} px)", "h", "start")
    SX = (720 - 250) / S
    fl = d.y(zy(0))
    d.add(f'<line class="floor" x1="{d.x(-13):.1f}" y1="{fl:.1f}" x2="{d.x(SX + 13):.1f}" y2="{fl:.1f}"/>')
    e = shelf_edge()
    zb = BT - BAR_H
    cx, cy = cup_xy()
    g = GAP / 2

    for dx, view in ((0.0, "front"), (SX, "side")):
        d.text(d.x(dx), d.y(zy(zmax - 0.6)) - 4,
               ("FRONT (shelf corner at the left)" if view == "front" else "SIDE (shelf corner at the right)") if floor
               else ("FRONT" if view == "front" else "SIDE"), "h")
        if floor:
            if view == "front":
                d.rect(dx + SHELF_X0, zy(F_SHELF_TOP), dx - e, zy(F_SHELF_TOP - SHELF_T), "shelfp")
            else:
                d.rect(dx + e, zy(F_SHELF_TOP), dx + SHELF_Y1, zy(F_SHELF_TOP - SHELF_T), "shelfp")
        d.rect(dx - g, zy(BT), dx + g, zy(zb), "ap")                       # one cross member face-on
        d.rect(dx - LEG_T / 2, zy(H), dx + LEG_T / 2, zy(0), "post")      # the far/near pair, edge-on
        for sg in (-1, 1):                                                 # the face-on pair, splayed
            d.poly(leg_poly(sg, H, dx, zy), "post")
        d.rect(dx - GHOST_D / 2, zy(BT + GHOST_H), dx + GHOST_D / 2, zy(BT), "ghost")
        px = cx if view == "front" else cy
        base = F_SHELF_TOP if floor else 0.0
        d.rect(dx + px - CUP_D / 2, zy(base + CUP_H), dx + px + CUP_D / 2, zy(base), "cup")
        d.text(d.x(dx), d.y(zy(BT + GHOST_H / 2)), "BOROUX 3-gal", "n")
        d.text(d.x(dx), d.y(zy(BT + GHOST_H / 2)) + 14, f"base ⌀{frac(GHOST_D)} × {frac(GHOST_H)}", "n")

    xr = d.x(outer(0, H)) + 40
    d.dim_v(zy(H), zy(0), xr, f"{frac(H)} legs", pxo=d.x(outer(H, H)) + 4, left=False)
    d.dim_v(zy(BT), zy(0), xr + 36, f"{frac(BT)} X top", pxo=d.x(inner(BT, H)) + 4, left=False)
    xl = d.x(-outer(0, H)) - 40
    d.dim_v(zy(BT), zy(zb), xl, f"{frac(BAR_H)} bar", pxo=d.x(-inner(BT, H)) - 4)
    d.dim_v(zy(H), zy(BT), xl - 36, f"{frac(H - BT)} post", pxo=d.x(-inner(H, H)) - 4)
    if floor:
        d.dim_v(zy(F_SHELF_TOP), zy(0), xl - 72, f"{frac(F_SHELF_TOP)} shelf top", pxo=d.x(-outer(0, H)) - 4)
    yb = fl + 30
    d.dim_h(-outer(0, H), outer(0, H), yb, f"{frac(2 * outer(0, H))} outside (the legs are vertical)", pyo=fl, below=True)
    d.dim_h(-inner(0, H), inner(0, H), yb + 30, f"{frac(2 * inner(0, H))} between legs at the feet", pyo=fl, below=True)
    d.dim_h(-inner(H, H), inner(H, H), yb + 60, f"{frac(2 * inner(H, H))} between legs at the tops", pyo=fl, below=True)
    d.text(20, HGT - 34, f"Dashed grey = a BOROUX 3-Gallon (base ⌀{frac(GHOST_D)}, {frac(GHOST_H)} tall) sitting on the X. Dashed red = a 30 oz tumbler"
           + (" on the shelf." if floor else " on the counter."), "n", "start")
    d.text(20, HGT - 18, f"The legs are vertical and {frac(W_TOP)} wide at the top; the inside face is plumb to the X, then tapers outward to {frac(leg_w(0, H))} at the foot. "
           "The cup stands in the corner, in front of or behind the X, not under it.", "n", "start")
    d.save(path, f"{name}, front and side elevations", EXTRA)


# ===========================================================================
# Plan
# ===========================================================================
def plan(path, floor=True):
    H = F_H if floor else C_H
    BT = F_BAR_TOP if floor else C_BAR_TOP
    S = 22
    Wd, Hd = 880, 760
    d = Drawing(Wd, Hd, 400, 385, s=S)
    name = "Floor stand" if floor else "Countertop stand"
    d.text(20, 26, f"{name} — plan, looking down (1 in = {S} px)", "h", "start")
    zm = BT - BAR_H / 2
    t = LEG_T / 2
    if floor:
        d.poly(shelf_pts(), "shelfp")
        d.text(d.x(-6.2), d.y(8.2), "shelf", "n")
    for sg in (-1, 1):   # feet, dashed
        for (xa, ya, xb, yb_) in ((min(sg * inner(0, H), sg * outer(0, H)), -t, max(sg * inner(0, H), sg * outer(0, H)), t),
                                  (-t, min(sg * inner(0, H), sg * outer(0, H)), t, max(sg * inner(0, H), sg * outer(0, H)))):
            d.add(f'<rect class="hid" x="{d.x(xa):.1f}" y="{d.y(ya):.1f}" width="{(xb - xa) * S:.1f}" height="{(yb_ - ya) * S:.1f}"/>')
    g = GAP / 2
    d.rect(-g, -BAR_T / 2, g, BAR_T / 2, "ap")           # the X
    d.rect(-BAR_T / 2, -g, BAR_T / 2, g, "ap")
    for sg in (-1, 1):   # leg tops
        xa, xb = sorted((sg * inner(H, H), sg * outer(H, H)))
        d.rect(xa, -t, xb, t, "post")
        d.rect(-t, xa, t, xb, "post")
    d.add(f'<circle class="ghost" cx="{d.x(0):.1f}" cy="{d.y(0):.1f}" r="{GHOST_D / 2 * S:.1f}"/>')
    d.text(d.x(2.2), d.y(-1.2), "filter on the X", "t")
    d.text(d.x(2.2), d.y(-1.2) + 14, f"base ⌀{frac(GHOST_D)}", "n")
    nx, ny = nozzle_xy()
    bx, by = nozzle_xy(GHOST_D / 2)
    d.add(f'<line x1="{d.x(bx):.1f}" y1="{d.y(by):.1f}" x2="{d.x(nx):.1f}" y2="{d.y(ny):.1f}" stroke="#6b7885" stroke-width="5" stroke-dasharray="5 3"/>')
    cx, cy = cup_xy()
    d.add(f'<circle class="cup" cx="{d.x(cx):.1f}" cy="{d.y(cy):.1f}" r="{CUP_D / 2 * S:.1f}"/>')
    d.text(d.x(cx), d.y(cy) + 4, "cup", "n")
    ttop = d.y(-outer(0, H)) - 24
    d.dim_h(-outer(0, H), outer(0, H), ttop, f"{frac(2 * outer(0, H))} outside (legs vertical)", pyo=d.y(-t))
    d.dim_h(-inner(0, H), inner(0, H), ttop - 30, f"{frac(2 * inner(0, H))} between legs at the feet (dashed)", pyo=d.y(-t))
    d.dim_h(-inner(H, H), inner(H, H), d.y(outer(H, H)) + 90, f"{frac(2 * inner(H, H))} between legs at the tops", pyo=d.y(0))
    d.text(20, Hd - 52, "Four legs at the compass points; the two cross members (the X) are half-lapped at the centre and Domino'd into the legs' plumb inside faces.", "n", "start")
    d.text(20, Hd - 36, "The filter's base ring (dashed circle) drops between the legs and sits on the X; the legs stand above it as posts.", "n", "start")
    d.text(20, Hd - 20, "Spigot faces the shelf corner (diagonal, dashed grey bar); the cup stands on the shelf under it." if floor
           else "Spigot faces the open diagonal; the cup stands on the counter under it.", "n", "start")
    d.save(path, f"{name}, plan view", EXTRA)


# ===========================================================================
# Parts / joinery sheet (floor stand)
# ===========================================================================
def parts(path):
    H, BT = F_H, F_BAR_TOP
    d = Drawing(1060, 760, 0, 0, s=12)
    d.text(20, 26, "Floor stand — parts and joinery. Countertop stand: the same parts, shorter legs.", "h", "start")
    lx, ly, sc = 90, 80, 7.5
    px = lambda x: lx + x * sc
    pz = lambda z: ly + (H - z) * sc
    lx0 = lx + 30
    px = lambda x: lx0 + x * sc
    pts = [(px(x - GAP / 2), pz(z)) for x, z in [(GAP / 2 + W_TOP, H), (GAP / 2, H), (GAP / 2, kink(H)),
                                                  (inner(0, H), 0), (outer(0, H), 0)]]
    d.add('<polygon class="post" points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + '"/>')
    d.text(lx, ly - 14, "LEG ×4 (inside face on the left; draw it 1:1 for a template)", "h", "start")
    zm = BT - BAR_H / 2
    for sgn in (-1, 1):
        zc = zm + sgn * DOM_PITCH / 2
        d.add(f'<rect class="cut" x="{px(0):.1f}" y="{pz(zc + DOM_W / 2):.1f}" width="{DOM_DEPTH * sc:.1f}" height="{DOM_W * sc:.1f}"/>')
    xr_ = px(outer(0, H) - GAP / 2) + 24
    d.leader(px(DOM_DEPTH), pz(zm), xr_, pz(zm) - 4,
             f"2 Domino mortises 8×40, centred {frac(zm)} up, {frac(DOM_PITCH)} apart (plumb face)")
    d.leader(px(0), pz(kink(H)), xr_, pz(kink(H)) + 24, f"inside face plumb to {frac(kink(H))}, then tapers")
    d.leader(px(outer(0, H) - GAP / 2), pz(0), xr_, pz(0) - 4, f"top and foot square; {frac(W_TOP)} wide at the top, {frac(leg_w(0, H))} at the foot")
    d.text(lx, pz(0) + 22, f"blank {frac(LEG_BLANK_W)} × {frac(LEG_T)} × about {frac(H + 0.5)}", "n", "start")
    d.text(lx, pz(0) + 38, "outside edge: plumb;", "n", "start")
    d.text(lx, pz(0) + 54, "inside edge: plumb to the X, then one taper out", "n", "start")
    sx0, sy0, sc2 = 640, 100, 40
    d.text(sx0, sy0 - 28, "LEG section at the mortise (×40/12)", "h", "start")
    ww = leg_w(zm, H)
    d.add(f'<rect class="post" x="{sx0}" y="{sy0}" width="{ww * sc2:.1f}" height="{LEG_T * sc2}"/>')
    d.add(f'<rect class="cut" x="{sx0}" y="{sy0 + (LEG_T - DOM_T) / 2 * sc2:.1f}" width="{DOM_DEPTH * sc2:.1f}" height="{DOM_T * sc2:.1f}"/>')
    d.text(sx0, sy0 + LEG_T * sc2 + 16, f"{frac(ww)} × {frac(LEG_T)}; Domino mortise (8 mm, 20 mm deep) on the inside face (left)", "n", "start")
    ax, ay = 460, 250
    d.text(ax, ay - 14, "CROSS MEMBERS ×2 (the X), half-lapped at the centre", "h", "start")
    L = bar_len(BT, H)
    sB = 8
    for k, (label, notch_bottom) in enumerate((("A: notch from the underside", True), ("B: notch from the top", False))):
        y0 = ay + k * 110
        d.add(f'<rect class="ap" x="{ax:.1f}" y="{y0:.1f}" width="{L * sB:.1f}" height="{BAR_H * sB:.1f}"/>')
        for xx in (ax, ax + (L - DOM_DEPTH) * sB):          # the Domino mortises in the bar ends (hidden)
            for sgn in (-1, 1):
                zc = BAR_H / 2 + sgn * DOM_PITCH / 2
                d.add(f'<rect class="hid" x="{xx:.1f}" y="{y0 + (zc - DOM_W / 2) * sB:.1f}" width="{DOM_DEPTH * sB:.1f}" height="{DOM_W * sB:.1f}"/>')
        nx0 = ax + (L / 2 - BAR_T / 2) * sB
        ny0 = y0 + BAR_H / 2 * sB if notch_bottom else y0
        d.add(f'<rect class="cut" x="{nx0:.1f}" y="{ny0:.1f}" width="{BAR_T * sB:.1f}" height="{BAR_H / 2 * sB:.1f}"/>')
        d.text(ax, y0 + BAR_H * sB + 16, f"{label}: lap {frac(BAR_T)} wide × {frac(BAR_H / 2)} deep, centred", "n", "start")
    d.text(ax, ay + 110 + BAR_H * sB + 34, f"{frac(BAR_T)} × {frac(BAR_H)} × {frac(L)}; two 8×40 Dominos in each end (dashed), {frac(DOM_PITCH)} apart", "n", "start")
    d.text(ax, ay + 110 + BAR_H * sB + 50, "square ends butt the plumb inside faces", "n", "start")
    sx, sy, s3 = 90, 470, 18
    d.text(sx, sy - 18, "SHELF ×1 (floor stand only)", "h", "start")
    e = shelf_edge()
    pts = [(sx + (x - SHELF_X0) * s3, sy + (SHELF_Y1 - y) * s3) for x, y in shelf_pts()]
    d.add('<polygon class="shelfp" points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + '"/>')
    w, h = -e - SHELF_X0, SHELF_Y1 - e
    d.add(f'<line class="dim" x1="{sx:.1f}" y1="{sy + h * s3 + 16:.1f}" x2="{sx + w * s3:.1f}" y2="{sy + h * s3 + 16:.1f}" marker-start="url(#a)" marker-end="url(#a)"/>')
    d.text(sx + w * s3 / 2, sy + h * s3 + 32, f"{frac(w)} × {frac(h)} × {frac(SHELF_T)}", "t")
    d.text(sx + w * s3 + 20, sy + 30, "bottom edge butts the leg on the x axis,", "n", "start")
    d.text(sx + w * s3 + 20, sy + 46, "right edge butts the leg on the y axis;", "n", "start")
    d.text(sx + w * s3 + 20, sy + 62, "one 5×30 Domino in each of those edges,", "n", "start")
    d.text(sx + w * s3 + 20, sy + 78, "centred on the leg, into mortises in the leg face; glued", "n", "start")
    d.text(sx + w * s3 + 20, sy + 94, f"chamfer {frac(SHELF_CHAMF)} on the outer corner", "n", "start")
    d.save(path, "Floor stand parts and joinery", EXTRA)


# ===========================================================================
# Isometric renderings (concept views from the plan dimensions)
# ===========================================================================
def shade(hex_, f):
    h = hex_.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(v * f))) for v in (r, g, b))


class Iso:
    C, SN = math.cos(math.radians(30)), 0.5

    def __init__(self, w, h, ox, oy, k):
        self.w, self.h, self.ox, self.oy, self.k, self.items = w, h, ox, oy, k, []

    def P(self, x, y, z):
        return (self.ox + (x - y) * self.C * self.k, self.oy + (x + y) * self.SN * self.k - z * self.k)

    def _poly(self, pts, fill, sw=1.1):
        s = " ".join(f"{a:.1f},{b:.1f}" for a, b in (self.P(*q) for q in pts))
        return f'<polygon points="{s}" fill="{fill}" stroke="#3a2815" stroke-width="{sw}" stroke-linejoin="round"/>'

    def hexa(self, bot, top, color, key):
        """bot/top: 4 corners each, order (x-,y-) (x+,y-) (x+,y+) (x-,y+) as (x,y,z).
        Draws the +x face, +y face and top (the three the camera sees)."""
        def draw():
            b0, b1, b2, b3 = bot
            t0, t1, t2, t3 = top
            return (self._poly([b1, b2, t2, t1], shade(color, .78)) +
                    self._poly([b2, b3, t3, t2], shade(color, .90)) +
                    self._poly([t0, t1, t2, t3], shade(color, 1.05)))
        self.items.append((key, draw))

    def box(self, x0, x1, y0, y1, z0, z1, color, key=None):
        bot = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)]
        top = [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        self.hexa(bot, top, color, ((x0 + x1) / 2 + (y0 + y1) / 2) if key is None else key)

    def prism(self, pts, z0, z1, color, key):
        """Extruded polygon (counter-clockwise from above); draws the faces the camera sees."""
        def draw():
            out = ""
            n = len(pts)
            for i in range(n):
                (xa, ya), (xb, yb) = pts[i], pts[(i + 1) % n]
                nx, ny = (yb - ya), -(xb - xa)
                if nx + ny > 1e-9:
                    f = .78 if nx > ny else .90
                    out += self._poly([(xa, ya, z0), (xb, yb, z0), (xb, yb, z1), (xa, ya, z1)], shade(color, f))
            out += self._poly([(x, y, z1) for x, y in pts], shade(color, 1.05))
            return out
        self.items.append((key, draw))

    def ellipse(self, cx, cy, z, r):
        a, b = self.P(cx, cy, z)
        return a, b, r * self.C * math.sqrt(2) * self.k, r * self.SN * math.sqrt(2) * self.k

    def cylinder(self, cx, cy, z0, z1, r, fill, key, r_top=None, stroke="#4b5560"):
        def draw():
            rt = r if r_top is None else r_top
            xb, yb, rxb, ryb = self.ellipse(cx, cy, z0, r)
            xt, yt, rxt, ryt = self.ellipse(cx, cy, z1, rt)
            return (f'<path d="M{xb-rxb:.1f},{yb:.1f} L{xt-rxt:.1f},{yt:.1f} A{rxt:.1f},{ryt:.1f} 0 0 1 {xt+rxt:.1f},{yt:.1f} '
                    f'L{xb+rxb:.1f},{yb:.1f} A{rxb:.1f},{ryb:.1f} 0 0 1 {xb-rxb:.1f},{yb:.1f} Z" fill="{fill}" stroke="{stroke}" stroke-width="1.1"/>'
                    f'<ellipse cx="{xt:.1f}" cy="{yt:.1f}" rx="{rxt:.1f}" ry="{ryt:.1f}" fill="url(#lid)" stroke="{stroke}" stroke-width="1.1"/>')
        self.items.append((key, draw))

    def save(self, path, title, notes=()):
        body = "".join(fn() for _, fn in sorted(self.items, key=lambda t: t[0]))
        defs = ('<defs><linearGradient id="steel" x1="0" x2="1"><stop offset="0" stop-color="#9aa4ad"/><stop offset=".35" stop-color="#eef1f3"/>'
                '<stop offset=".7" stop-color="#c3cbd2"/><stop offset="1" stop-color="#7f8a94"/></linearGradient>'
                '<linearGradient id="lid" x1="0" x2="1"><stop offset="0" stop-color="#d7dde2"/><stop offset="1" stop-color="#aab3bb"/></linearGradient></defs>')
        txt = "".join(f'<text x="20" y="{self.h-18-14*(len(notes)-1-i)}" font-family="Helvetica Neue,Arial,sans-serif" font-size="12" fill="#444">{n}</text>'
                       for i, n in enumerate(notes))
        with open(path, "w", encoding="utf-8") as f:
            f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                    f'width="{self.w}" height="{self.h}" role="img" aria-label="{title}"><title>{title}</title>{defs}'
                    f'<rect width="{self.w}" height="{self.h}" fill="#fff"/>{body}{txt}</svg>\n')


WOOD = "#c98b57"       # cherry-ish
WOOD2 = "#d9a06a"


def leg3d(iso, axis, sg, H):
    """One tapered leg, in two pieces: plumb inside face above the kink, tapered below."""
    t = LEG_T / 2
    k = kink(H)

    def corners(a, b, z):
        lo, hi = sorted((a, b))
        if axis == "x":
            return [(lo, -t, z), (hi, -t, z), (hi, t, z), (lo, t, z)]
        return [(-t, lo, z), (t, lo, z), (t, hi, z), (-t, hi, z)]
    key = sg * (inner(H, H) + outer(H, H)) / 2
    iso.hexa(corners(sg * inner(0, H), sg * outer(0, H), 0), corners(sg * inner(k, H), sg * outer(k, H), k), WOOD, key)
    iso.hexa(corners(sg * inner(k, H), sg * outer(k, H), k), corners(sg * inner(H, H), sg * outer(H, H), H), WOOD, key + 0.001)


def build_iso(path, floor):
    H = F_H if floor else C_H
    BT = F_BAR_TOP if floor else C_BAR_TOP
    iso = Iso(780, 760 if floor else 640, 390, 650 if floor else 500, 9.5 if floor else 15.0)
    zm = BT - BAR_H / 2
    g = GAP / 2
    iso.box(-g, g, -BAR_T / 2, BAR_T / 2, BT - BAR_H, BT, WOOD2, 0.01)
    iso.box(-BAR_T / 2, BAR_T / 2, -g, g, BT - BAR_H, BT, WOOD2, 0.02)
    for sg in (-1, 1):
        leg3d(iso, "x", sg, H)
        leg3d(iso, "y", sg, H)
    cx, cy = cup_xy()
    if floor:
        iso.prism(shelf_pts(), F_SHELF_TOP - SHELF_T, F_SHELF_TOP, "#e5c08e", 0.0)
        iso.cylinder(cx, cy, F_SHELF_TOP, F_SHELF_TOP + CUP_H, CUP_D / 2, "url(#steel)", cx + cy + 0.5, r_top=CUP_D / 2 + 0.2)
    else:
        iso.prism([(-9.5, -9), (9.5, -9), (9.5, 11), (-9.5, 11)], -0.6, 0, "#d8dce0", -40)
        iso.cylinder(cx, cy, 0, CUP_H, CUP_D / 2, "url(#steel)", cx + cy + 0.5, r_top=CUP_D / 2 + 0.2)
    r = GHOST_D / 2
    iso.cylinder(0, 0, BT, BT + 1.0, min(r + 0.1, GAP / 2 - 0.02), "#26292c", 0.5, stroke="#111")
    iso.cylinder(0, 0, BT + 1.0, BT + GHOST_H, r, "url(#steel)", 0.51)
    nx, ny = nozzle_xy()
    bx, by = nozzle_xy(r - 0.2)
    iso.box(min(bx, nx) - 0.35, max(bx, nx) + 0.35, min(by, ny) - 0.35, max(by, ny) + 0.35,
            BT + SPIGOT_UP - 0.4, BT + SPIGOT_UP + 0.4, "#2a2d30", 0.52)
    ttl = "Floor" if floor else "Countertop"
    iso.save(path, f"{ttl} water-filter stand with a BOROUX 3-Gallon, three-quarter concept view",
             ["Concept rendering drawn from the plan dimensions — cherry-toned; not a photograph.",
              (f"Filter on the X at {frac(BT)}, legs {frac(H)}, shelf at {frac(F_SHELF_TOP)} with a tumbler under the spigot. BOROUX 3-Gallon, 23″ tall."
               if floor else f"Filter on the X at {frac(BT)}, legs {frac(H)}; a tumbler stands on the counter under the spigot.")])


# ===========================================================================
def report():
    for nm, H, BT in (("Floor", F_H, F_BAR_TOP),):
        print(f"{nm} stand: legs {frac(LEG_T)} thick, {frac(W_TOP)} wide at the top, {frac(leg_w(0, H))} wide at the foot, {frac(H)} vertical, inside face plumb above {frac(kink(H))}")
        print(f"  tops: {frac(GAP)} between, {frac(2 * outer(H, H))} outside; feet: {frac(2 * inner(0, H))} between, {frac(2 * outer(0, H))} outside")
        print(f"  X top {frac(BT)}, bars {frac(BAR_T)} x {frac(BAR_H)} x {frac(bar_len(BT, H))} long, butts the legs; two 8x40 Dominos per end centred {frac(BT - BAR_H / 2)} up")
        print(f"  legs vertical; inside edge below the kink tapers outward {math.degrees(math.atan(S_IN)):.2f} deg")
    e = shelf_edge()
    print(f"Shelf: {frac(-e - SHELF_X0)} x {frac(SHELF_Y1 - e)} x {frac(SHELF_T)}, top {frac(F_SHELF_TOP)}")
    com = F_BAR_TOP + 10
    diag = (outer(0, F_H) + LEG_T / 2) / math.sqrt(2)      # distance to the line joining adjacent feet's outer corners
    print(f"Tip: floor stand, CoM ~{com:.0f}: along a leg axis {math.degrees(math.atan(outer(0, F_H) / com)):.1f} deg, diagonal {math.degrees(math.atan(diag / com)):.1f} deg")
    for name, dia, h in MODELS:
        gap = (GAP - dia) / 2
        gapt = gap
        print(f"  {name:26s} dia {dia:5.2f} h {h:5.2f}  slack each side {gap:5.2f}  total on floor {F_BAR_TOP+h:5.1f}")


def main():
    os.makedirs(OUT, exist_ok=True)
    assert abs(inner(F_H, F_H) * 2 - GAP) < 1e-9
    assert inner(0, F_H) > GAP / 2 and leg_w(0, F_H) < W_TOP, "the legs must narrow toward the foot"
    cx, cy = cup_xy()          # the cup must sit on the shelf and clear both leg lines
    assert -cx + CUP_D / 2 <= -SHELF_X0 and cy + CUP_D / 2 <= SHELF_Y1, "cup hangs off the shelf"
    assert -cx - CUP_D / 2 >= shelf_edge() and cy - CUP_D / 2 >= shelf_edge(), "cup overlaps a leg line"
    assert GHOST_D <= GAP + 1e-9, "filter ring does not fit between the legs"
    for nm, H, BT in (("floor", F_H, F_BAR_TOP),):
        wmin = leg_w(BT - BAR_H / 2 - (DOM_PITCH + DOM_W) / 2, H)       # narrowest leg section a Domino mortise passes through
        assert DOM_DEPTH < wmin - 0.75, f"{nm}: Domino mortise leaves too little wood in the leg"
        assert DOM_PITCH + DOM_W < BAR_H, f"{nm}: two Dominos don't fit the bar's height"
        assert DOM_T < BAR_T / 2 and DOM_T < LEG_T / 2, "Domino too thick for the bar or leg"
    assert SH_W + 0.5 < leg_w(F_SHELF_TOP, F_H), "the shelf Domino doesn't fit across the leg face"
    w = lambda n: os.path.join(OUT, n)
    elevations(w("water-stand-floor-elevations.svg"), True)
    plan(w("water-stand-floor-plan.svg"), True)
    parts(w("water-stand-floor-parts.svg"))
    build_iso(w("water-stand-floor-render.svg"), True)
    report()


if __name__ == "__main__":
    main()
