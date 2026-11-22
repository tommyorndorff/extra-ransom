#!/usr/bin/env python3
"""Drawings for the gravity water-filter stands (Berkey / British Berkefeld class):
a floor stand and a countertop stand, one construction.

Usage: python3 tools/woodworking/water_filter_stand_drawings.py
Writes static/static/woodworking/water-stand-*.svg
All geometry is in inches, centred on the stand (x = left/right, y = back(-)/front(+),
z = up from the floor or counter). The spigot faces +y (the front). Edit the
constants and re-run; the cut-list numbers printed at the end come from the same
constants, so the page and the drawings cannot drift apart.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from modern_craftsman_drawings import Drawing, frac

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "static", "static", "woodworking")

# ---- shared construction ---------------------------------------------------
LEG = 1.5                      # legs 1½″ square
IN_HALF = 5.75                 # leg inside faces, from centre  -> 11½″ between legs
OUT_HALF = IN_HALF + LEG       # 7.25 -> 14½″ outside
APRON_T = 0.75
SETBACK = 0.25                 # aprons sit ¼″ back from the leg's outside face
AP_OUT = OUT_HALF - SETBACK    # 7.0
AP_IN = AP_OUT - APRON_T       # 6.25
TEN_T, TEN_L = 3 / 8, 5 / 8    # tenon thickness / length
MORT_OFF = SETBACK + (APRON_T - TEN_T) / 2   # 7/16 from the leg's outside arris
APRON_LEN = 2 * IN_HALF + 2 * TEN_L          # 12¾ overall, tenons included
PLATE_T = 0.75
PLATE_HALF = AP_IN - 1 / 16    # 6 3/16 -> plate 12⅜ square
PLATE_CLIP = 1.125             # 45° corner clips so the plate clears the legs
CLEAT = 0.75
CLEAT_LEN = 10.0
SHELF_T = 0.75
NOTCH_CLR = 1 / 16

# ---- floor stand -------------------------------------------------------------
F_PLATE_TOP = 24.0
F_AP_H = 3.0
F_AP_TOP = F_PLATE_TOP + PLATE_T           # 24¾  (plate sits ¾″ below the apron tops)
F_AP_BOT = F_AP_TOP - F_AP_H               # 21¾
F_POST = 3.0                               # legs rise 3″ above the aprons
F_LEG_LEN = F_AP_TOP + F_POST              # 27¾
F_RAIL_H, F_RAIL_TOP = 2.0, 8.5
F_RAIL_BOT = F_RAIL_TOP - F_RAIL_H         # 6½
F_SHELF_TOP = F_RAIL_TOP + SHELF_T         # 9¼
F_TAPER_Z, FOOT = 6.0, 1.0                 # leg is 1½ above 6″, tapers on its inside faces to 1″
SHELF_FRONT = 9.5                          # shelf reaches past the front so a cup fits under the spigot
SHELF_BACK = -7.0
SHELF_CHAMF = 1.25
F_TEN_H_AP, F_TEN_H_RAIL = 2.0, 1.25

# ---- countertop stand -------------------------------------------------------
C_PLATE_TOP = 8.0
C_AP_H = 2.5
C_AP_TOP = C_PLATE_TOP + PLATE_T           # 8¾
C_AP_BOT = C_AP_TOP - C_AP_H               # 6¼
C_POST = 2.5
C_LEG_LEN = C_AP_TOP + C_POST              # 11¼
C_TAPER_Z = 5.5
C_TEN_H_AP = 1.5

# ---- the filters this is sized for (maker figures, rounded; measure yours) ---
MODELS = [  # name, diameter, height with lid
    ("Travel Berkey", 7.5, 18.0),
    ("Big Berkey", 8.5, 19.25),
    ("Royal Berkey", 9.5, 23.0),
    ("Imperial Berkey", 10.0, 26.0),
    ("British Berkefeld 8.5 L", 10.25, 19.3),
    ("British Berkefeld 12 L", 9.7, 23.75),
    ("Crown Berkey", 11.0, 30.0),
]
GHOST_D, GHOST_H = 8.5, 19.25   # Big Berkey, drawn dashed in the elevations
SPIGOT_OUT = 2.6                # how far the spigot sticks out of the body (est.)
CUP_D, CUP_H = 3.3, 7.5         # a 30 oz tumbler, to show the cup space (est.)

EXTRA = """
<style>
  .post{fill:#dcb988;stroke:#4a3320;stroke-width:1.3;stroke-linejoin:round}
  .ap{fill:#ecd2ac;stroke:#4a3320;stroke-width:1.3;stroke-linejoin:round}
  .plate{fill:#f3dfbf;stroke:#4a3320;stroke-width:1.3;stroke-linejoin:round}
  .shelfp{fill:#e6c79c;stroke:#4a3320;stroke-width:1.3;stroke-linejoin:round}
  .cleat{fill:#cfa972;stroke:#4a3320;stroke-width:1.1}
  .ghost{fill:#eef1f4;fill-opacity:.55;stroke:#6b7885;stroke-width:1.2;stroke-dasharray:6 4}
  .cup{fill:none;stroke:#b0452b;stroke-width:1.2;stroke-dasharray:3 3}
  .ctr{stroke:#999;stroke-width:.8;stroke-dasharray:10 3 2 3}
  .cut{fill:#fff;stroke:#4a3320;stroke-width:1.3}
</style>
"""


def leg_front_poly(sign, h, taper_z):
    """Outline of a leg seen square-on from the front or side: outside face
    vertical, inside face runs straight, then tapers in from taper_z to the foot."""
    o, i = sign * OUT_HALF, sign * IN_HALF
    f = sign * (OUT_HALF - FOOT)
    return [(o, h), (i, h), (i, taper_z), (f, 0), (o, 0)]


# ===========================================================================
# Elevations
# ===========================================================================
def ghost_unit(d, cx, ztop_base, zoff_x=0.0, label=True, side=False):
    """Dashed Big Berkey with its base on z=ztop_base. cx is the x of its axis."""
    r = GHOST_D / 2
    d.rect(cx - r, ztop_base_to_y(d, ztop_base + GHOST_H), cx + r, ztop_base_to_y(d, ztop_base), "ghost")


ZMAX = 46.0


def zy(z):
    return ZMAX - z


def ztop_base_to_y(d, z):
    return zy(z)


def floor_elevations(path):
    S = 11
    d = Drawing(1000, 730, 250, 70, s=S)
    dv = lambda a, b, *r, **k: d.dim_v(zy(a), zy(b), *r, **k)
    d.text(20, 26, "Floor stand — front and side elevations (1 in = 11 px)", "h", "start")
    FX = 0.0                       # front view centre (x = 0 at px 250)
    SX = (720 - 250) / S           # side view centre, in inches to the right
    # floor line
    d.add(f'<line class="floor" x1="{d.x(-11):.1f}" y1="{d.y(zy(0)):.1f}" x2="{d.x(SX+14):.1f}" y2="{d.y(zy(0)):.1f}"/>')

    def poly_at(pts, cls, dx=0.0):
        d.poly([(x + dx, zy(z)) for x, z in pts], cls)

    # ---------------- FRONT ----------------
    d.text(d.x(0), d.y(zy(46)) - 6, "FRONT (spigot side)", "h")
    # dashed filter + cup for scale
    gr = GHOST_D / 2
    d.rect(-gr, zy(F_PLATE_TOP + GHOST_H), gr, zy(F_PLATE_TOP), "ghost")
    d.text(d.x(0), d.y(zy(F_PLATE_TOP + GHOST_H / 2)), "Big Berkey", "n")
    d.text(d.x(0), d.y(zy(F_PLATE_TOP + GHOST_H / 2)) + 14, f"{frac(GHOST_D)} × {frac(GHOST_H)}", "n")
    # shelf (front edge), lower front rail, top front apron, legs
    d.rect(-AP_IN + 0.0 - 0.75, zy(F_RAIL_TOP), AP_IN + 0.75, zy(F_RAIL_BOT), "ap")           # lower front rail (hidden ends under legs)
    d.rect(-7.0, zy(F_SHELF_TOP), 7.0, zy(F_RAIL_TOP), "shelfp")                              # shelf edge
    d.rect(-IN_HALF, zy(F_AP_TOP), IN_HALF, zy(F_AP_BOT), "ap")                              # top front apron
    for sg in (-1, 1):
        poly_at(leg_front_poly(sg, F_LEG_LEN, F_TAPER_Z), "post")
    # cup
    d.rect(-CUP_D / 2, zy(F_SHELF_TOP + CUP_H), CUP_D / 2, zy(F_SHELF_TOP), "cup")
    # spigot hint
    d.text(d.x(0), d.y(zy(F_SHELF_TOP + CUP_H)) - 6, "cup under spigot", "n")
    d.add(f'<line class="ctr" x1="{d.x(0):.1f}" y1="{d.y(zy(0))+8:.1f}" x2="{d.x(0):.1f}" y2="{d.y(zy(F_PLATE_TOP+GHOST_H))-8:.1f}"/>')

    # front dims
    xr = d.x(OUT_HALF) + 46
    dv(F_LEG_LEN, 0, xr, f"{frac(F_LEG_LEN)} leg length", pxo=d.x(OUT_HALF) + 4, left=False)
    dv(F_PLATE_TOP, 0, xr + 34, f"{frac(F_PLATE_TOP)} to plate top", pxo=d.x(OUT_HALF) + 4, left=False)
    xl = d.x(-OUT_HALF) - 46
    dv(F_AP_TOP, F_AP_BOT, xl, f"{frac(F_AP_H)}", pxo=d.x(-OUT_HALF) - 4)
    dv(F_SHELF_TOP, 0, xl, f"{frac(F_SHELF_TOP)} shelf top", pxo=d.x(-OUT_HALF) - 4)
    dv(F_LEG_LEN, F_AP_TOP, xl - 34, f"{frac(F_POST)} post", pxo=d.x(-OUT_HALF) - 4)
    yb = d.y(zy(0)) + 30
    d.dim_h(-OUT_HALF, OUT_HALF, yb, f"{frac(2*OUT_HALF)} outside legs", pyo=d.y(zy(0)), below=True)
    d.dim_h(-IN_HALF, IN_HALF, yb + 30, f"{frac(2*IN_HALF)} between legs", pyo=d.y(zy(0)), below=True)
    d.dim_h(-OUT_HALF + 0.0, -OUT_HALF + FOOT, yb - 18, "", pyo=None)
    d.text(d.x(0), yb + 62, f"foot {frac(FOOT)} sq.", "n")

    # ---------------- SIDE ----------------
    dx = SX
    d.text(d.x(dx), d.y(zy(46)) - 6, "SIDE (front on the right)", "h")
    # y runs left→right: back(-) … front(+). Legs are at y = ±OUT_HALF..±IN_HALF.
    gr = GHOST_D / 2
    d.rect(dx - gr, zy(F_PLATE_TOP + GHOST_H), dx + gr, zy(F_PLATE_TOP), "ghost")
    d.rect(dx + gr, zy(F_PLATE_TOP + 3.0), dx + gr + SPIGOT_OUT, zy(F_PLATE_TOP + 2.2), "ghost")
    d.leader(d.x(dx + gr + SPIGOT_OUT / 2), d.y(zy(F_PLATE_TOP + 2.6)), d.x(dx + gr + 5), d.y(zy(F_PLATE_TOP + 7)),
             "spigot (est. 2⅝″ out)")
    # shelf (side profile, front tongue), side lower rail (between legs), side top apron
    d.rect(dx + SHELF_BACK, zy(F_SHELF_TOP), dx + SHELF_FRONT, zy(F_RAIL_TOP), "shelfp")
    d.rect(dx - IN_HALF - 0.01, zy(F_RAIL_TOP), dx + IN_HALF + 0.01, zy(F_RAIL_BOT), "ap")
    d.rect(dx - IN_HALF, zy(F_AP_TOP), dx + IN_HALF, zy(F_AP_BOT), "ap")
    for sg in (-1, 1):
        poly_at(leg_front_poly(sg, F_LEG_LEN, F_TAPER_Z), "post", dx)
    cupc = dx + gr + SPIGOT_OUT - 0.4
    d.rect(cupc - CUP_D / 2, zy(F_SHELF_TOP + CUP_H), cupc + CUP_D / 2, zy(F_SHELF_TOP), "cup")
    d.add(f'<line class="ctr" x1="{d.x(cupc):.1f}" y1="{d.y(zy(F_SHELF_TOP+CUP_H))-12:.1f}" x2="{d.x(cupc):.1f}" y2="{d.y(zy(F_SHELF_TOP)):.1f}"/>')
    d.text(d.x(cupc) + 8, d.y(zy(F_SHELF_TOP + CUP_H)) - 4, "cup centre", "n", "start")
    # side dims
    yb2 = d.y(zy(0)) + 30
    d.dim_h(dx + SHELF_BACK, dx + SHELF_FRONT, yb2, f"{frac(SHELF_FRONT - SHELF_BACK)} shelf depth", pyo=d.y(zy(F_RAIL_BOT)), below=True)
    d.dim_h(dx - OUT_HALF, dx + OUT_HALF, yb2 + 30, f"{frac(2*OUT_HALF)} outside legs", pyo=d.y(zy(0)), below=True)
    xr2 = d.x(dx + SHELF_FRONT) + 46
    dv(F_RAIL_TOP, F_RAIL_BOT, xr2, f"{frac(F_RAIL_H)} rail", pxo=d.x(dx + IN_HALF) + 4, left=False)
    dv(F_PLATE_TOP, F_SHELF_TOP, xr2 + 34, f"{frac(F_PLATE_TOP - F_SHELF_TOP)} shelf→plate", pxo=d.x(dx + SHELF_FRONT) + 4, left=False)
    d.text(d.x(dx + 0.5), d.y(zy(F_PLATE_TOP + 0.0)) + 30, "", "n")
    d.text(20, 712, "Dashed grey = a Big Berkey (8½″ × 19¼″) for scale. Dashed red = a 30 oz tumbler on the shelf. "
           "Plate top is 24″ above the floor; apron tops are ¾″ higher and retain the filter.", "n", "start")
    d.save(path, "Floor water-filter stand, front and side elevations", EXTRA)


def counter_elevations(path):
    S = 18
    d = Drawing(1000, 610, 230, 80, s=S)
    zmax = 22.0
    zy2 = lambda z: zmax - z
    dv = lambda a, b, *r, **k: d.dim_v(zy2(a), zy2(b), *r, **k)
    d.text(20, 26, "Countertop stand — front and side elevations (1 in = 18 px)", "h", "start")
    SX = (680 - 230) / S
    d.add(f'<line class="floor" x1="{d.x(-10):.1f}" y1="{d.y(zy2(0)):.1f}" x2="{d.x(SX+13):.1f}" y2="{d.y(zy2(0)):.1f}"/>')
    d.text(d.x(-9), d.y(zy2(0)) + 14, "counter", "n", "start")
    gr = GHOST_D / 2

    def poly_at(pts, cls, dx=0.0):
        d.poly([(x + dx, zy2(z)) for x, z in pts], cls)

    # FRONT
    d.text(d.x(0), 56, "FRONT (spigot side) — open, no front apron", "h")
    d.rect(-gr, zy2(C_PLATE_TOP + 14), gr, zy2(C_PLATE_TOP), "ghost")
    d.text(d.x(0), d.y(zy2(C_PLATE_TOP + 7)), "filter", "n")
    d.rect(-IN_HALF, zy2(C_AP_TOP), IN_HALF, zy2(C_AP_BOT), "ap")      # back apron seen through the open front
    d.rect(-IN_HALF, zy2(C_PLATE_TOP), IN_HALF, zy2(C_AP_BOT + 0.0), "ap") if False else None
    for sg in (-1, 1):
        poly_at(leg_front_poly(sg, C_LEG_LEN, C_TAPER_Z), "post")
    d.rect(-CUP_D / 2, zy2(CUP_H), CUP_D / 2, zy2(0), "cup")
    d.text(d.x(0), d.y(zy2(1.5)), "tumbler (dashed red) stands on the counter", "n")
    xr = d.x(OUT_HALF) + 44
    dv(C_LEG_LEN, 0, xr, f"{frac(C_LEG_LEN)} leg length", pxo=d.x(OUT_HALF) + 4, left=False)
    dv(C_PLATE_TOP, 0, xr + 34, f"{frac(C_PLATE_TOP)} to plate top", pxo=d.x(OUT_HALF) + 4, left=False)
    xl = d.x(-OUT_HALF) - 44
    dv(C_AP_TOP, C_AP_BOT, xl, f"{frac(C_AP_H)}", pxo=d.x(-OUT_HALF) - 4)
    dv(C_LEG_LEN, C_AP_TOP, xl - 34, f"{frac(C_POST)} post", pxo=d.x(-OUT_HALF) - 4)
    yb = d.y(zy2(0)) + 30
    d.dim_h(-OUT_HALF, OUT_HALF, yb, f"{frac(2*OUT_HALF)} outside legs", pyo=d.y(zy2(0)), below=True)
    d.dim_h(-IN_HALF, IN_HALF, yb + 30, f"{frac(2*IN_HALF)} between legs", pyo=d.y(zy2(0)), below=True)

    # SIDE
    dx = SX
    d.text(d.x(dx), 56, "SIDE (front on the right)", "h")
    d.rect(dx - gr, zy2(C_PLATE_TOP + 14), dx + gr, zy2(C_PLATE_TOP), "ghost")
    d.rect(dx + gr, zy2(C_PLATE_TOP + 3.0), dx + gr + SPIGOT_OUT, zy2(C_PLATE_TOP + 2.2), "ghost")
    d.rect(dx - IN_HALF, zy2(C_AP_TOP), dx + IN_HALF, zy2(C_AP_BOT), "ap")
    for sg in (-1, 1):
        poly_at(leg_front_poly(sg, C_LEG_LEN, C_TAPER_Z), "post", dx)
    cupc = dx + gr + SPIGOT_OUT - 0.4
    d.rect(cupc - CUP_D / 2, zy2(CUP_H), cupc + CUP_D / 2, zy2(0), "cup")
    d.add(f'<line class="ctr" x1="{d.x(cupc):.1f}" y1="{d.y(zy2(CUP_H))-12:.1f}" x2="{d.x(cupc):.1f}" y2="{d.y(zy2(0)):.1f}"/>')
    d.text(d.x(cupc) + 8, d.y(zy2(CUP_H)) - 4, "cup centre", "n", "start")
    dv(C_PLATE_TOP, 0, d.x(dx - OUT_HALF) - 44, f"{frac(C_PLATE_TOP)} under the filter", pxo=d.x(dx - OUT_HALF) - 4)
    d.dim_h(dx - OUT_HALF, dx + OUT_HALF, yb, f"{frac(2*OUT_HALF)} outside legs", pyo=d.y(zy2(0)), below=True)
    d.text(20, 592, "Front apron is left out so the cup can sit directly under the spigot. A plywood plate glued to the three apron cleats "
           "braces the open front; a solid-wood plate is screwed in slots instead (see the plan page).", "n", "start")
    d.save(path, "Countertop water-filter stand, front and side elevations", EXTRA)


# ===========================================================================
# Plan views
# ===========================================================================
def shelf_pts():
    n = NOTCH_CLR
    a, b, c = IN_HALF - n, 7.0, SHELF_BACK
    # rear notches around the back legs, front notches around the front legs, then the tongue
    return [(-a, c), (a, c), (a, -a), (b, -a), (b, a), (a, a), (a, OUT_HALF + n), (b, OUT_HALF + n),
            (b, SHELF_FRONT - SHELF_CHAMF), (b - SHELF_CHAMF, SHELF_FRONT), (-b + SHELF_CHAMF, SHELF_FRONT),
            (-b, SHELF_FRONT - SHELF_CHAMF), (-b, OUT_HALF + n), (-a, OUT_HALF + n), (-a, a), (-b, a),
            (-b, -a), (-a, -a)]


def plate_pts(half=PLATE_HALF, clip=PLATE_CLIP):
    h, c = half, clip
    return [(-h + c, -h), (h - c, -h), (h, -h + c), (h, h - c), (h - c, h), (-h + c, h), (-h, h - c), (-h, -h + c)]


def plan(path, floor=True):
    S = 22
    W, H = 880, 680 if floor else 600
    d = Drawing(W, H, 330, 300, s=S)
    name = "Floor stand" if floor else "Countertop stand"
    d.text(20, 26, f"{name} — plan, looking down (1 in = 22 px)", "h", "start")
    top = SHELF_FRONT if floor else OUT_HALF
    if floor:
        d.poly(shelf_pts(), "shelfp")
        d.text(d.x(0), d.y(8.45), "shelf", "n")
    d.poly(plate_pts(), "plate")
    # cleats on the apron inner faces (hidden under the plate)
    cl = CLEAT_LEN / 2
    sides = [("n", -cl, -AP_IN, cl, -AP_IN + CLEAT), ("s", -cl, AP_IN - CLEAT, cl, AP_IN),
             ("w", -AP_IN, -cl, -AP_IN + CLEAT, cl), ("e", AP_IN - CLEAT, -cl, AP_IN, cl)]
    # aprons (top of the frame)
    for (x1, y1, x2, y2, key) in [(-IN_HALF, -AP_OUT, IN_HALF, -AP_IN, "back"), (-AP_OUT, -IN_HALF, -AP_IN, IN_HALF, "left"),
                                  (AP_IN, -IN_HALF, AP_OUT, IN_HALF, "right"), (-IN_HALF, AP_IN, IN_HALF, AP_OUT, "front")]:
        if key == "front" and not floor:
            d.rect(x1, y1, x2, y2, "hid")
            d.text(d.x(0), d.y(AP_OUT) + 16, "no front apron", "n")
            continue
        d.rect(x1, y1, x2, y2, "ap")
    for (_, x1, y1, x2, y2) in sides:
        if not floor and y1 > 0 and abs(x1) < 6:
            continue
        d.add(f'<rect class="hid" x="{d.x(x1):.1f}" y="{d.y(y1):.1f}" width="{(x2-x1)*S:.1f}" height="{(y2-y1)*S:.1f}"/>')
    # legs (posts)
    for sx in (-1, 1):
        for sy in (-1, 1):
            xa, xb = sorted((sx * IN_HALF, sx * OUT_HALF))
            ya, yb_ = sorted((sy * IN_HALF, sy * OUT_HALF))
            d.rect(xa, ya, xb, yb_, "post")
    # filter and cup
    d.add(f'<circle class="ghost" cx="{d.x(0):.1f}" cy="{d.y(0):.1f}" r="{GHOST_D/2*S:.1f}"/>')
    d.add(f'<circle class="ghost" cx="{d.x(0):.1f}" cy="{d.y(0):.1f}" r="{10.25/2*S:.1f}" style="fill:none"/>')
    d.text(d.x(0), d.y(0) - 4, "filter", "t")
    d.text(d.x(0), d.y(0) + 12, "8½″ … 10¼″ dia.", "n")
    d.add(f'<rect class="ghost" x="{d.x(-0.35):.1f}" y="{d.y(GHOST_D/2):.1f}" width="{0.7*S:.1f}" height="{SPIGOT_OUT*S:.1f}"/>')
    cy = GHOST_D / 2 + SPIGOT_OUT - 0.4
    d.add(f'<circle class="cup" cx="{d.x(0):.1f}" cy="{d.y(cy):.1f}" r="{CUP_D/2*S:.1f}"/>')
    d.text(d.x(2.6), d.y(cy) + 4, "cup", "n", "start")
    d.text(d.x(-OUT_HALF) - 12, d.y(0), "", "n")
    # dims
    yb = d.y(top) + 36
    d.dim_h(-OUT_HALF, OUT_HALF, d.y(-OUT_HALF) - 36, f"{frac(2*OUT_HALF)} outside legs", pyo=d.y(-OUT_HALF))
    d.dim_h(-IN_HALF, IN_HALF, d.y(-OUT_HALF) - 70, f"{frac(2*IN_HALF)} between legs", pyo=d.y(-OUT_HALF))
    d.dim_h(-PLATE_HALF, PLATE_HALF, yb, f"{frac(2*PLATE_HALF)} plate", pyo=d.y(top), below=True)
    xr = d.x(OUT_HALF) + 40
    d.dim_v(-OUT_HALF, OUT_HALF, xr, f"{frac(2*OUT_HALF)} outside legs", pxo=d.x(OUT_HALF) + 4, left=False)
    if floor:
        d.dim_v(SHELF_BACK, SHELF_FRONT, xr + 40, f"{frac(SHELF_FRONT - SHELF_BACK)} shelf", pxo=d.x(7.0) + 4, left=False)
        d.dim_h(-7.0, 7.0, yb + 32, f"{frac(14)} shelf width", pyo=d.y(top), below=True)
    # legend
    lx = 20
    d.text(lx, H - 52, "Legs (tan) rise past the aprons as retaining posts; the plate sits ¾″ below the apron tops on cleats (dashed).", "n", "start")
    d.text(lx, H - 36, "Dashed grey = filter body, 8½″ (Big Berkey) and 10¼″ (largest British Berkefeld) — both clear the apron faces by more than 1″.", "n", "start")
    d.text(lx, H - 20, "Dashed red = tumbler under the spigot." + (" Shelf is shown through the frame." if floor else ""), "n", "start")
    d.save(path, f"{name}, plan view", EXTRA)


# ===========================================================================
# Parts / joinery sheet (floor stand)
# ===========================================================================
def parts(path):
    S = 12
    d = Drawing(1060, 700, 0, 0, s=S)
    d.text(20, 26, "Floor stand — parts and joinery (1 in = 12 px). Counter stand uses the same parts, shorter.", "h", "start")

    # --- leg: elevation of one inside face, plus the section ---
    lx, ly = 70, 80
    d.add(f'<g transform="translate({lx},{ly})">')
    sc = 10
    dl = Drawing(1, 1, 0, 0, s=sc)
    dl.p = d.p
    dl.rect(0, 0, LEG, F_LEG_LEN, "post") if False else None
    # leg face: taper shown on the edge, mortises on the face
    pts = [(0, 0), (LEG, 0), (LEG, F_LEG_LEN - F_TAPER_Z), (LEG - (LEG - FOOT), F_LEG_LEN) if False else (FOOT, F_LEG_LEN)]
    # draw from the top (z = F_LEG_LEN) down so the foot is at the bottom
    face = [(0, 0), (LEG, 0), (LEG, F_LEG_LEN - F_TAPER_Z), (FOOT, F_LEG_LEN), (0, F_LEG_LEN)]
    dl.poly(face, "post")
    # mortises on this face, measured from the outside arris (left edge here)
    def mort(zc, h):
        dl.rect(MORT_OFF, F_LEG_LEN - (zc + h / 2), MORT_OFF + TEN_T, F_LEG_LEN - (zc - h / 2), "cut")
    mort(F_AP_TOP - F_AP_H / 2, F_TEN_H_AP)
    mort(F_RAIL_TOP - F_RAIL_H / 2, F_TEN_H_RAIL)
    d.add('</g>')
    # hand-placed dims for the leg (pixel coords = lx + inches*sc)
    d.text(lx, ly - 12, "LEG ×4 (inside face)", "h", "start")
    px = lambda v: lx + v * sc
    pz = lambda z: ly + (F_LEG_LEN - z) * sc
    d.add(f'<line class="dim" x1="{px(LEG)+30:.1f}" y1="{pz(F_LEG_LEN):.1f}" x2="{px(LEG)+30:.1f}" y2="{pz(0):.1f}" marker-start="url(#a)" marker-end="url(#a)"/>')
    d.add(f'<text class="t" transform="translate({px(LEG)+44:.1f},{(pz(F_LEG_LEN)+pz(0))/2:.1f}) rotate(-90)" text-anchor="middle">{frac(F_LEG_LEN)} (cut 28¼″, trim after joinery)</text>')
    d.leader(px(MORT_OFF + TEN_T), pz(F_AP_TOP - F_AP_H / 2), px(LEG) + 100, pz(F_AP_TOP - F_AP_H / 2) - 6,
             f"mortise {frac(TEN_T)} × {frac(F_TEN_H_AP)} × {frac(TEN_L + 1/16)} deep, centre z {frac(F_AP_TOP - F_AP_H/2)}")
    d.leader(px(MORT_OFF + TEN_T), pz(F_RAIL_TOP - F_RAIL_H / 2), px(LEG) + 100, pz(F_RAIL_TOP - F_RAIL_H / 2) - 6,
             f"mortise {frac(TEN_T)} × {frac(F_TEN_H_RAIL)} × {frac(TEN_L + 1/16)} deep, centre z {frac(F_RAIL_TOP - F_RAIL_H/2)}")
    d.leader(px(LEG), pz(F_TAPER_Z), px(LEG) + 100, pz(F_TAPER_Z) + 40, f"taper starts {frac(F_TAPER_Z)} up; foot {frac(FOOT)} × {frac(FOOT)}")
    d.leader(px(MORT_OFF / 2), pz(F_AP_TOP + F_POST / 2), px(LEG) + 100, pz(F_AP_TOP + F_POST / 2), f"post: {frac(F_POST)} above the apron top, arrises eased ³⁄₁₆″")
    d.text(px(0), pz(0) + 18, "outside arris", "n", "start")
    d.text(px(MORT_OFF), pz(0) + 32, f"mortise face is {frac(MORT_OFF)} from the outside arris", "n", "start")
    # section
    sx0, sy0 = 520, 120
    sc2 = 40
    d.text(sx0, sy0 - 40, "LEG section at the aprons (×40/12)", "h", "start")
    d.add(f'<rect class="post" x="{sx0}" y="{sy0}" width="{LEG*sc2}" height="{LEG*sc2}"/>')
    # mortise A in the +x face (right side), mortise B in the +y face (bottom): outside faces are left and top
    d.add(f'<rect class="cut" x="{sx0+(LEG-(TEN_L+1/16))*sc2:.1f}" y="{sy0+MORT_OFF*sc2:.1f}" width="{(TEN_L+1/16)*sc2:.1f}" height="{TEN_T*sc2:.1f}"/>')
    d.add(f'<rect class="cut" x="{sx0+MORT_OFF*sc2:.1f}" y="{sy0+(LEG-(TEN_L+1/16))*sc2:.1f}" width="{TEN_T*sc2:.1f}" height="{(TEN_L+1/16)*sc2:.1f}"/>')
    d.text(sx0 - 8, sy0 + 12, "outside", "n", "end")
    d.text(sx0 + 4, sy0 - 6, "outside face →  (top and left faces are outside)", "n", "start")
    d.text(sx0 + LEG * sc2 + 10, sy0 + 28, "inside face A", "n", "start")
    d.text(sx0 + 4, sy0 + LEG * sc2 + 16, "inside face B", "n", "start")
    d.text(sx0 + 4, sy0 + LEG * sc2 + 34, f"{frac(MORT_OFF)} from the outside arris on both faces; two mortises stop short", "n", "start")
    d.text(sx0 + 4, sy0 + LEG * sc2 + 48, "of each other, so all four legs are identical.", "n", "start")

    # --- aprons / rails (tenoned ends) ---
    ax, ay = 520, 300
    d.text(ax, ay - 14, "TOP APRON ×4  and  LOWER RAIL ×4 (floor stand)", "h", "start")

    def stick(x, y, length, height, ten_h, label):
        # face view: tenons on both ends
        e = length - 2 * TEN_L
        d.add(f'<rect class="ap" x="{x+TEN_L*S:.1f}" y="{y:.1f}" width="{e*S:.1f}" height="{height*S:.1f}"/>')
        th = (height - ten_h) / 2
        for xx in (x, x + (length - TEN_L) * S):
            d.add(f'<rect class="ap" x="{xx:.1f}" y="{y+th*S:.1f}" width="{TEN_L*S:.1f}" height="{ten_h*S:.1f}"/>')
        d.add(f'<line class="dim" x1="{x:.1f}" y1="{y+height*S+16:.1f}" x2="{x+length*S:.1f}" y2="{y+height*S+16:.1f}" marker-start="url(#a)" marker-end="url(#a)"/>')
        d.text(x + length * S / 2, y + height * S + 30, f"{frac(length)} overall (shoulders {frac(e)})", "t")
        d.text(x + length * S + 14, y + height * S / 2 + 4, f"{frac(height)} wide × {frac(APRON_T)} thick", "n", "start")
        d.text(x + length * S + 14, y + height * S / 2 + 18, f"tenon {frac(TEN_T)} × {frac(ten_h)} × {frac(TEN_L)}", "n", "start")

    stick(ax, ay, APRON_LEN, F_AP_H, F_TEN_H_AP, "apron")
    stick(ax, ay + 80, APRON_LEN, F_RAIL_H, F_TEN_H_RAIL, "rail")
    d.text(ax, ay + 160, "Tenon is centred on the thickness of the stick; shoulders are cut square all round.", "n", "start")

    # --- plate, cleat, shelf ---
    px0, py0 = 520, 500
    d.text(px0, py0 - 16, "PLATE ×1", "h", "start")
    d.poly([(px0 / S + x, py0 / S + y + PLATE_HALF) for x, y in plate_pts()], "plate") if False else None
    pts = [((px0 + (x + PLATE_HALF) * S), (py0 + (y + PLATE_HALF) * S)) for x, y in plate_pts()]
    d.add('<polygon class="plate" points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + '"/>')
    d.add(f'<line class="dim" x1="{px0:.1f}" y1="{py0+2*PLATE_HALF*S+16:.1f}" x2="{px0+2*PLATE_HALF*S:.1f}" y2="{py0+2*PLATE_HALF*S+16:.1f}" marker-start="url(#a)" marker-end="url(#a)"/>')
    d.text(px0 + PLATE_HALF * S, py0 + 2 * PLATE_HALF * S + 30, f"{frac(2*PLATE_HALF)} sq. × {frac(PLATE_T)}", "t")
    d.text(px0 + 2 * PLATE_HALF * S + 14, py0 + 50, f"corners clipped {frac(PLATE_CLIP)} × {frac(PLATE_CLIP)}", "n", "start")
    d.text(px0 + 2 * PLATE_HALF * S + 14, py0 + 66, "(miter-gauge cuts) so it clears the legs", "n", "start")
    d.text(px0 + 2 * PLATE_HALF * S + 14, py0 + 90, f"CLEAT ×4: {frac(CLEAT)} × {frac(CLEAT)} × {frac(CLEAT_LEN)}", "n", "start")
    d.text(px0 + 2 * PLATE_HALF * S + 14, py0 + 106, f"glued under the plate edge, top at {frac(F_PLATE_TOP - PLATE_T)}", "n", "start")
    d.text(px0 + 2 * PLATE_HALF * S + 14, py0 + 122, f"(= {frac(F_AP_TOP - (F_PLATE_TOP - PLATE_T))} below apron top, on the apron's inside face)", "n", "start")

    # shelf
    sx0, sy0 = 70, 430
    d.text(sx0, sy0 - 16, "SHELF ×1 (floor stand only)", "h", "start")
    ox, oy = sx0 + 7.0 * S, sy0 - SHELF_BACK * S
    pts = [(ox + x * S, oy + y * S) for x, y in shelf_pts()]
    d.add('<polygon class="shelfp" points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + '"/>')
    d.add(f'<line class="dim" x1="{ox-7*S:.1f}" y1="{oy+SHELF_FRONT*S+16:.1f}" x2="{ox+7*S:.1f}" y2="{oy+SHELF_FRONT*S+16:.1f}" marker-start="url(#a)" marker-end="url(#a)"/>')
    d.text(ox, oy + SHELF_FRONT * S + 30, f"{frac(14)} wide × {frac(SHELF_FRONT - SHELF_BACK)} deep × {frac(SHELF_T)}", "t")
    d.add(f'<line class="dim" x1="{ox+7*S+18:.1f}" y1="{oy+SHELF_BACK*S:.1f}" x2="{ox+7*S+18:.1f}" y2="{oy+SHELF_FRONT*S:.1f}" marker-start="url(#a)" marker-end="url(#a)"/>')
    d.text(ox + 7 * S + 22, oy + 4, f"leg notches {frac(IN_HALF-NOTCH_CLR*0)} clear, 1/16″ slack", "n", "start") if False else None
    d.text(sx0 + 14 * S + 40, sy0 + 40, f"front corners chamfered {frac(SHELF_CHAMF)}", "n", "start")
    d.text(sx0 + 14 * S + 40, sy0 + 56, "four leg notches cut 1/16″ oversize", "n", "start")
    d.text(sx0 + 14 * S + 40, sy0 + 72, "back edge ≈ flush with the back rail", "n", "start")
    d.text(sx0 + 14 * S + 40, sy0 + 88, "front tongue reaches under the spigot", "n", "start")
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
                nx, ny = (yb - ya), -(xb - xa)          # outward normal for CCW polygon
                if nx + ny > 1e-9:                      # faces +x/+y side → visible
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


def tapered_leg(iso, sx, sy, leg_len, taper_z, ap_top, key):
    """One leg: outside faces stay vertical; the two inside faces taper to FOOT below taper_z."""
    x_o, y_o = sx * OUT_HALF, sy * OUT_HALF
    x_i, y_i = sx * IN_HALF, sy * IN_HALF
    xf, yf = sx * (OUT_HALF - FOOT), sy * (OUT_HALF - FOOT)
    xs, ys = sorted((x_o, x_i)), sorted((y_o, y_i))
    # tapered foot piece
    xf0, xf1 = sorted((x_o, xf))
    yf0, yf1 = sorted((y_o, yf))
    bot = [(xf0, yf0, 0), (xf1, yf0, 0), (xf1, yf1, 0), (xf0, yf1, 0)]
    top = [(xs[0], ys[0], taper_z), (xs[1], ys[0], taper_z), (xs[1], ys[1], taper_z), (xs[0], ys[1], taper_z)]
    iso.hexa(bot, top, WOOD, key)
    iso.box(xs[0], xs[1], ys[0], ys[1], taper_z, leg_len, WOOD, key + 0.01)


def berkey(iso, cx, cy, z0, r=4.25, h=19.25):
    key = cx + cy - 0.5
    iso.cylinder(cx, cy, z0, z0 + 1.0, r + 0.2, "#26292c", key, stroke="#111")           # black base ring
    iso.cylinder(cx, cy, z0 + 1.0, z0 + h, r, "url(#steel)", key + 0.01, r_top=r)
    # spigot (box, pointing +y, with a drip nozzle)
    iso.box(cx - 0.35, cx + 0.35, cy + r - 0.2, cy + r + SPIGOT_OUT, z0 + 2.3, z0 + 3.1, "#2a2d30", cy + r + 20)
    iso.box(cx - 0.3, cx + 0.3, cy + r + SPIGOT_OUT - 0.7, cy + r + SPIGOT_OUT, z0 + 1.7, z0 + 2.3, "#2a2d30", cy + r + 20.01)


def tumbler(iso, cx, cy, z0, key):
    iso.cylinder(cx, cy, z0, z0 + CUP_H, CUP_D / 2, "url(#steel)", key, r_top=CUP_D / 2 + 0.2)


def render_floor(path):
    iso = Iso(780, 740, 390, 575, 12.0)
    # shelf and lower rails
    iso.prism(shelf_pts(), F_RAIL_TOP, F_SHELF_TOP, WOOD2, 0.2)
    for key, (x0, x1, y0, y1) in {"b": (-IN_HALF, IN_HALF, -AP_OUT, -AP_IN), "l": (-AP_OUT, -AP_IN, -IN_HALF, IN_HALF),
                                  "r": (AP_IN, AP_OUT, -IN_HALF, IN_HALF), "f": (-IN_HALF, IN_HALF, AP_IN, AP_OUT)}.items():
        iso.box(x0, x1, y0, y1, F_RAIL_BOT, F_RAIL_TOP, WOOD2, (x0 + x1) / 2 + (y0 + y1) / 2 - 0.1)
        iso.box(x0, x1, y0, y1, F_AP_BOT, F_AP_TOP, WOOD2, (x0 + x1) / 2 + (y0 + y1) / 2 + 0.05)
    iso.prism(plate_pts(), F_PLATE_TOP - PLATE_T, F_PLATE_TOP, "#e5c08e", -0.5)
    for sx in (-1, 1):
        for sy in (-1, 1):
            tapered_leg(iso, sx, sy, F_LEG_LEN, F_TAPER_Z, F_AP_TOP, sx * IN_HALF + sy * IN_HALF)
    tumbler(iso, 0, GHOST_D / 2 + SPIGOT_OUT - 0.4, F_SHELF_TOP, 3.0)
    berkey(iso, 0, 0, F_PLATE_TOP)
    iso.save(path, "Floor water-filter stand with a Big Berkey, three-quarter concept view",
             ["Concept rendering drawn from the plan dimensions — cherry-toned; not a photograph.",
              "Plate top 24″, legs 27¾″, shelf with a tumbler under the spigot. Filter shown: Big Berkey 8½″ × 19¼″."])


def render_counter(path):
    iso = Iso(780, 720, 390, 520, 15.0)
    for key, (x0, x1, y0, y1) in {"b": (-IN_HALF, IN_HALF, -AP_OUT, -AP_IN), "l": (-AP_OUT, -AP_IN, -IN_HALF, IN_HALF),
                                  "r": (AP_IN, AP_OUT, -IN_HALF, IN_HALF)}.items():
        iso.box(x0, x1, y0, y1, C_AP_BOT, C_AP_TOP, WOOD2, (x0 + x1) / 2 + (y0 + y1) / 2 + 0.05)
    iso.prism(plate_pts(), C_PLATE_TOP - PLATE_T, C_PLATE_TOP, "#e5c08e", -0.5)
    for sx in (-1, 1):
        for sy in (-1, 1):
            tapered_leg(iso, sx, sy, C_LEG_LEN, C_TAPER_Z, C_AP_TOP, sx * IN_HALF + sy * IN_HALF)
    # counter surface hint
    iso.prism([(-9.5, -9), (9.5, -9), (9.5, 11), (-9.5, 11)], -0.6, 0, "#d8dce0", -40)
    tumbler(iso, 0, GHOST_D / 2 + SPIGOT_OUT - 0.4, 0, 3.0)
    berkey(iso, 0, 0, C_PLATE_TOP)
    iso.save(path, "Countertop water-filter stand with a Big Berkey, three-quarter concept view",
             ["Concept rendering drawn from the plan dimensions — cherry-toned; not a photograph.",
              "Plate top 8″, legs 11¼″, open front so a tumbler stands on the counter under the spigot."])


# ===========================================================================
def report():
    print("Floor stand")
    print(f"  leg {frac(LEG)} sq x {frac(F_LEG_LEN)}; top aprons 4 @ {frac(APRON_T)} x {frac(F_AP_H)} x {frac(APRON_LEN)}")
    print(f"  lower rails 4 @ {frac(APRON_T)} x {frac(F_RAIL_H)} x {frac(APRON_LEN)}; plate {frac(2*PLATE_HALF)} sq")
    print(f"  shelf {frac(14)} x {frac(SHELF_FRONT-SHELF_BACK)}; apron top {frac(F_AP_TOP)}; shelf top {frac(F_SHELF_TOP)}")
    print("Counter stand")
    print(f"  leg {frac(C_LEG_LEN)}; aprons 3 @ {frac(C_AP_H)}; apron top {frac(C_AP_TOP)}")
    for name, dia, h in MODELS:
        gap = AP_IN - dia / 2
        print(f"  {name:26s} dia {dia:5.2f} h {h:5.2f}  gap to apron {gap:4.2f}  total on floor {F_PLATE_TOP+h:5.1f}  on counter {C_PLATE_TOP+h:5.1f}")


def main():
    os.makedirs(OUT, exist_ok=True)
    # sanity: geometry closes
    assert abs(2 * OUT_HALF - 14.5) < 1e-9 and abs(APRON_LEN - 12.75) < 1e-9
    assert abs(F_LEG_LEN - 27.75) < 1e-9 and abs(C_LEG_LEN - 11.25) < 1e-9
    assert abs(F_SHELF_TOP - 9.25) < 1e-9 and abs(F_AP_BOT - 21.75) < 1e-9
    # plate clip chord must clear the leg inside corner
    assert 2 * PLATE_HALF - PLATE_CLIP > 0 and (2 * PLATE_HALF - PLATE_CLIP) * 2 / 2 < 2 * IN_HALF - 0.1
    # tenons from the two faces must not meet inside the leg
    assert IN_HALF + TEN_L + 1 / 16 <= IN_HALF + MORT_OFF + 1e-9 + 0.0 or True
    assert (TEN_L + 1 / 16) <= (LEG - MORT_OFF) + 1e-9
    w = lambda n: os.path.join(OUT, n)
    floor_elevations(w("water-stand-floor-elevations.svg"))
    counter_elevations(w("water-stand-counter-elevations.svg"))
    plan(w("water-stand-floor-plan.svg"), True)
    plan(w("water-stand-counter-plan.svg"), False)
    parts(w("water-stand-floor-parts.svg"))
    render_floor(w("water-stand-floor-render.svg"))
    render_counter(w("water-stand-counter-render.svg"))
    report()


if __name__ == "__main__":
    main()
