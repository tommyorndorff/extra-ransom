#!/usr/bin/env python3
"""True-scale SVGs for the jeweler's traveling tool chest plan.

Usage: python3 tools/woodworking/jewelers_chest_drawings.py
Writes static/static/woodworking/jewelers-chest-{front,section,tray,drawers}.svg
Geometry in inches (heights measured up from the floor, then flipped for the SVG).
Edit the constants, re-run.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from modern_craftsman_drawings import Drawing

K = 24                      # px per inch
W, D = 22.0, 12.0           # overall footprint (derived: design choice)
WALL = 0.5                  # case sides, back, well front
BOT_T, SHELF_T = 0.75, 0.75
BAY = 7.0                   # drawer bay, floor of opening to underside of shelf
RAIL = 0.5                  # rail between the two drawers
DR_OPEN = (BAY - RAIL) / 2  # 3.25
REVEAL = 1 / 16
DR_H = DR_OPEN - 2 * REVEAL # 3 3/16
DR_FRONT_T = 0.75
DR_SIDE_T = 0.375
DR_BOX_D = 10.75            # front face to back of drawer box
CASE_H = 13.0
LID_T = 0.75
TOTAL_H = CASE_H + LID_T    # 13.75
WELL_FRONT_H = CASE_H - (BOT_T + BAY + SHELF_T)   # 4.5
SHELF_TOP = BOT_T + BAY + SHELF_T                 # 8.5
CLEAT_TOP = 10.75
TRAY_H = 1.75
INNER_W = W - 2 * WALL      # 21
TRAY_W, TRAY_D = 20.75, 10.75
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "static", "static", "woodworking")


def fy(h):                  # height above floor -> drawing y (inches, down)
    return TOTAL_H - h


def front(path):
    d = Drawing(780, 520, 110, 95, s=K)
    d.text(20, 24, "Front elevation — 1 in = 24 px", "h", "start")
    # lid, case sides
    d.rect(0, fy(TOTAL_H), W, fy(CASE_H), "wood")
    d.rect(0, fy(CASE_H), WALL, fy(0), "leg")
    d.rect(W - WALL, fy(CASE_H), W, fy(0), "leg")
    # well front board
    d.rect(WALL, fy(CASE_H), W - WALL, fy(SHELF_TOP), "face")
    # shelf edge (through tenons show at the sides), bottom board
    d.rect(WALL, fy(SHELF_TOP), W - WALL, fy(BOT_T + BAY), "wood")
    d.rect(WALL, fy(BOT_T), W - WALL, fy(0), "wood")
    # drawer fronts
    x1, x2 = WALL + REVEAL, W - WALL - REVEAL
    b0 = BOT_T + REVEAL
    for lo in (b0, b0 + DR_OPEN + RAIL):
        d.rect(x1, fy(lo + DR_H), x2, fy(lo), "face")
        cx, cy = (x1 + x2) / 2, fy(lo + DR_H / 2)
        d.add(f'<circle class="pull" cx="{d.x(cx):.1f}" cy="{d.y(cy):.1f}" r="{0.3*K:.1f}"/>')
        d.add(f'<circle cx="{d.x(cx):.1f}" cy="{d.y(cy):.1f}" r="{0.15*K:.1f}" fill="#fff"/>')
    d.rect(x1, fy(BOT_T + DR_OPEN + RAIL), x2, fy(BOT_T + DR_OPEN), "wood")   # rail
    d.text(d.x(W / 2), d.y(fy(BOT_T + DR_OPEN + RAIL + DR_H)) - 4 + 0, "", "n")
    # lock escutcheon on the well front
    lx, ly = W / 2, fy(CASE_H - 0.9)
    d.rect(lx - 0.45, ly - 0.5, lx + 0.45, ly + 0.5, "pull")
    d.text(d.x(lx), d.y(ly) + 38, "half-mortise lid lock", "n")
    # handles on the sides (seen edge-on)
    d.rect(-0.55, fy(8.7), 0, fy(7.0), "pull")
    d.rect(W, fy(8.7), W + 0.55, fy(7.0), "pull")
    d.add(f'<line class="floor" x1="{d.x(-3):.1f}" y1="{d.y(fy(0)):.1f}" x2="{d.x(W+3):.1f}" y2="{d.y(fy(0)):.1f}"/>')
    # dimensions
    d.dim_h(0, W, 55, "22″ overall", pyo=d.y(0))
    d.dim_v(fy(TOTAL_H), fy(0), d.x(0) - 62, "13¾″ overall", pxo=d.x(0))
    d.dim_v(fy(TOTAL_H), fy(CASE_H), d.x(W) + 38, "¾″ lid", pxo=d.x(W))
    d.dim_v(fy(CASE_H), fy(SHELF_TOP), d.x(W) + 38, "4½″ well front", pxo=d.x(W), left=False)
    d.dim_v(fy(BOT_T + BAY), fy(BOT_T), d.x(W) + 38, "7″ drawer bay", pxo=d.x(W), left=False)
    d.dim_h(x1, x2, d.y(fy(0)) + 28, "drawer front 20⅞″ × 3³⁄₁₆″ (¹⁄₁₆″ reveals)", pyo=d.y(fy(0)), below=True)
    d.text(20, 500, "Bail handle on each end (dark blocks at the sides). Heights are above the floor; the lid is flush with the case front and back.", "n", "start")
    d.save(os.path.join(OUT, "jewelers-chest-front.svg"), "Jeweler's traveling chest, front elevation")


def section(path):
    d = Drawing(780, 540, 110, 100, s=K)
    d.text(20, 24, "Cross-section at centre, looking from the left end — 1 in = 24 px", "h", "start")
    # case walls: front well board, back, bottom, shelf
    d.rect(0, fy(CASE_H), WALL, fy(SHELF_TOP), "leg")                      # well front
    d.rect(D - WALL, fy(CASE_H - 0.75), D, fy(0), "leg")                   # back
    d.rect(0, fy(BOT_T), D - WALL, fy(0), "wood")                          # bottom
    d.rect(0, fy(SHELF_TOP), D - WALL, fy(BOT_T + BAY), "wood")            # shelf
    # lid (closed) with frame/panel hint
    d.rect(0, fy(TOTAL_H), D, fy(CASE_H), "wood")
    d.rect(2.0, fy(TOTAL_H - 0.25), D - 2.0, fy(TOTAL_H - 0.5), "hid")
    d.text(d.x(D / 2), d.y(fy(TOTAL_H)) - 8, "lid: ¾″ frame, ¼″ floating panel, bridle corners", "n")
    # cleats and tray
    d.rect(WALL, fy(CLEAT_TOP), WALL + 0.5, fy(CLEAT_TOP - 0.5), "spacer")
    d.rect(D - WALL - 0.5, fy(CLEAT_TOP), D - WALL, fy(CLEAT_TOP - 0.5), "spacer")
    d.rect(WALL + 0.125, fy(CLEAT_TOP + TRAY_H), D - WALL - 0.125, fy(CLEAT_TOP), "hid")
    d.text(d.x(D / 2), d.y(fy(CLEAT_TOP + 0.7)), "lift-out tray (1¾″ deep)", "n")
    d.text(d.x(D / 2), d.y(fy(SHELF_TOP + 1.2)), "well: hammers, mandrels, saw frame, torch tip kit", "n")
    # drawers (side section: front, box side as hidden)
    b0 = BOT_T + REVEAL
    for lo in (b0, b0 + DR_OPEN + RAIL):
        d.rect(0, fy(lo + DR_H), DR_FRONT_T, fy(lo), "face")
        d.rect(DR_FRONT_T, fy(lo + 3.0), DR_BOX_D, fy(lo + 0.25), "hid")
        d.rect(DR_FRONT_T, fy(lo + 0.25), DR_BOX_D, fy(lo), "pull")
        d.rect(0.0, fy(lo + DR_H), 0.0, fy(lo), "wood")
    d.rect(0, fy(BOT_T + DR_OPEN + RAIL), D - WALL, fy(BOT_T + DR_OPEN), "wood")   # full-depth rail
    d.text(d.x(5.5), d.y(fy(BOT_T + DR_OPEN + RAIL + 1.6)), "top drawer — soldering kit", "n")
    d.text(d.x(5.5), d.y(fy(BOT_T + 1.8)), "bottom drawer — lapidary kit", "n")
    # hinge + cord stay
    d.rect(D - 0.1, fy(CASE_H + 0.1), D + 0.2, fy(CASE_H - 0.5), "pull")
    d.text(d.x(D) + 10, d.y(fy(CASE_H)), "butt hinge (×2)", "n", "start")
    d.add(f'<line class="floor" x1="{d.x(-3):.1f}" y1="{d.y(fy(0)):.1f}" x2="{d.x(D+4):.1f}" y2="{d.y(fy(0)):.1f}"/>')
    # dims
    d.dim_h(0, D, 62, "12″ deep", pyo=d.y(fy(TOTAL_H)))
    d.dim_v(fy(CLEAT_TOP + TRAY_H), fy(SHELF_TOP), d.x(0) - 40, "shelf to tray rim 4″", pxo=d.x(0))
    d.dim_v(fy(CLEAT_TOP), fy(SHELF_TOP), d.x(D) + 60, "2¼″ under tray", pxo=d.x(D), left=False)
    d.dim_v(fy(TOTAL_H), fy(CASE_H), d.x(D) + 100, "¾″", pxo=d.x(D), left=False)
    d.dim_h(0, DR_BOX_D, d.y(fy(0)) + 28, "drawer 10¾″ front to back", pyo=d.y(fy(0)), below=True)
    d.text(20, 520, "Drawer sides ⅜″, bottoms ¼″ in a groove; ¾″ fronts. The ¾″ gap behind the drawers is a dust/stop space.", "n", "start")
    d.save(os.path.join(OUT, "jewelers-chest-section.svg"), "Jeweler's traveling chest, cross-section")


def tray(path):
    d = Drawing(780, 440, 70, 80, s=K)
    d.text(20, 24, "Lift-out tray, plan — 1 in = 24 px (tray interior 20⅛″ × 10⅛″)", "h", "start")
    d.rect(0, 0, TRAY_W, TRAY_D, "wood")
    zones = [
        (0.375, 0.375, 5.0, TRAY_D - 0.375, "pliers + cutters", "jaws up in a", "slotted block (8–10)"),
        (5.0, 0.375, 11.0, TRAY_D - 0.375, "files", "hand + needle files,", "two rows, 6–8″"),
        (11.0, 0.375, 15.75, TRAY_D - 0.375, "measuring", "dividers, calipers,", "rule, ring sizer"),
    ]
    for x1, y1, x2, y2, a, b, c in zones:
        d.rect(x1, y1, x2, y2, "face")
        d.text(d.x((x1 + x2) / 2), d.y((y1 + y2) / 2) - 6, a, "t")
        d.text(d.x((x1 + x2) / 2), d.y((y1 + y2) / 2) + 10, b, "n")
        d.text(d.x((x1 + x2) / 2), d.y((y1 + y2) / 2) + 24, c, "n")
    d.rect(15.75, 0.375, TRAY_W - 0.375, TRAY_D / 2, "face")
    d.text(d.x(18.0), d.y(2.5), "burnishers,", "n")
    d.text(d.x(18.0), d.y(2.5) + 14, "pushers, scribes", "n")
    d.rect(15.75, TRAY_D / 2, TRAY_W - 0.375, TRAY_D - 0.375, "face")
    d.text(d.x(18.0), d.y(8.0), "burs in index", "n")
    d.text(d.x(18.0), d.y(8.0) + 14, "cases, loupes", "n")
    d.dim_h(0, TRAY_W, 62, "20¾″ tray", pyo=d.y(0))
    d.dim_v(0, TRAY_D, d.x(0) - 30, "10¾″", pxo=d.x(0))
    d.text(20, 420, "Mitered ⅜″ sides, ¼″ bottom, ¼″ dividers; the front lip is cut down ½″ so the tools read at a glance.", "n", "start")
    d.save(os.path.join(OUT, "jewelers-chest-tray.svg"), "Jeweler's traveling chest, tray layout")


def drawers(path):
    iw, idp = 20.125, 9.625
    d = Drawing(780, 640, 70, 70, s=K)
    d.text(20, 24, "Drawer interiors, plan — 1 in = 24 px (each 20⅛″ × 9⅝″ × ≈2¾″ deep)", "h", "start")
    def box(y0, title):
        d.text(20, d.y(y0) - 8, title, "t", "start")
        d.rect(0, y0, iw, y0 + idp, "wood")
    box(0.0, "TOP — soldering kit")
    top = [
        (0.3, 0.3, 6.3, 9.3, "solder + flux", "sheet/wire in labeled", "tubes, flux bottle,", "borax dish"),
        (6.3, 0.3, 12.3, 9.3, "firing tools", "tweezers, third hand,", "ceramic tile, ring clamp,", "bench-pin inserts"),
        (12.3, 0.3, 19.8, 9.3, "finished + in-progress", "lidded boxes for rings,", "pendants and findings", "(no loose pieces)"),
    ]
    for x1, y1, x2, y2, a, b, c, e in top:
        d.rect(x1, y1, x2, y2, "face")
        mx, my = d.x((x1 + x2) / 2), d.y((y1 + y2) / 2)
        d.text(mx, my - 14, a, "t"); d.text(mx, my + 2, b, "n"); d.text(mx, my + 16, c, "n"); d.text(mx, my + 30, e, "n")
    y2 = idp + 2.6
    box(y2, "BOTTOM — lapidary teaching kit")
    bot = [
        (0.3, y2 + 0.3, 5.0, y2 + 9.3, "dops + wax", "dop sticks on edge", "in a slotted rack,", "wax, lamp tin"),
        (5.0, y2 + 0.3, 10.4, y2 + 9.3, "grit + polish", "sealed jars, one per grit;", "never share a lid or", "sponge between grits"),
        (10.4, y2 + 0.3, 15.4, y2 + 9.3, "templates + gauges", "templates, calipers,", "loupes, gem tweezers,", "wrapped stones"),
        (15.4, y2 + 0.3, 19.8, y2 + 9.3, "laps", "faceting laps in", "padded sleeves,", "flat (6″ discs)"),
    ]
    for x1, ya, x2, yb, a, b, c, e in bot:
        d.rect(x1, ya, x2, yb, "face")
        mx, my = d.x((x1 + x2) / 2), d.y((ya + yb) / 2)
        d.text(mx, my - 14, a, "t"); d.text(mx, my + 2, b, "n"); d.text(mx, my + 16, c, "n"); d.text(mx, my + 30, e, "n")
    d.text(20, 620, "Dividers are ¼″ and removable, so each kit can be rearranged for a different workshop.", "n", "start")
    d.save(os.path.join(OUT, "jewelers-chest-drawers.svg"), "Jeweler's traveling chest, drawer layouts")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    front(None); section(None); tray(None); drawers(None)
    print("wrote", OUT)
