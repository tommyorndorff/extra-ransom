#!/usr/bin/env python3
"""True-scale SVGs for the Picture Frame plan (1¼″ × ⅞″ profile, mitered, rabbeted).

Usage: python3 tools/woodworking/picture_frame_drawings.py
Writes static/static/woodworking/picture-frame-{front,profile,parts}.svg
Geometry in inches. Reuses the Drawing helper from modern_craftsman_drawings.py.
Edit the picture size / profile constants and re-run.
"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from modern_craftsman_drawings import Drawing, frac

# Profile (stated by the user)
FACE_W = 1.25          # width of the stock, seen from the front
FACE_T = 0.875         # height (thickness) of the stock
# Rabbet (chosen — see the plan page)
RAB_W, RAB_D = 0.375, 0.5
CLEAR = 1 / 16         # clearance per side between glass and rabbet wall
# Picture / glass (stated by the user): 11½ tall × 15⅝ wide
PIC_W, PIC_H = 15.625, 11.5
# Glass stack (chosen)
GLASS_T, PRINT_T, BACK_T = 0.125, 1 / 16, 0.125
# Stick
STICK_L = 72.0         # one 6′ length
KERF = 0.125           # saw kerf, measured square to the cut

LIP_T = FACE_T - RAB_D                      # 3/8 thick front lip
WALL = FACE_W - RAB_W                       # 7/8 wall behind the lip
RAB_OPEN_W, RAB_OPEN_H = PIC_W + 2 * CLEAR, PIC_H + 2 * CLEAR       # 15¾ × 11⅝
SIGHT_W, SIGHT_H = RAB_OPEN_W - 2 * RAB_W, RAB_OPEN_H - 2 * RAB_W   # 15 × 10⅞
OUT_W, OUT_H = SIGHT_W + 2 * FACE_W, SIGHT_H + 2 * FACE_W           # 17½ × 13⅜

S = 26


def front(path):
    d = Drawing(720, 580, 105, 120, s=S)
    d.text(20, 24, "Front elevation — 1 in = 26 px", "h", "start")
    d.rect(0, 0, OUT_W, OUT_H, "wood")
    # sight opening
    d.add(f'<rect class="bg" x="{d.x(FACE_W):.1f}" y="{d.y(FACE_W):.1f}" '
          f'width="{SIGHT_W*S:.1f}" height="{SIGHT_H*S:.1f}" stroke="#4a3320" stroke-width="1.3"/>')
    # miter seams
    for (x1, y1, x2, y2) in ((0, 0, FACE_W, FACE_W), (OUT_W, 0, OUT_W - FACE_W, FACE_W),
                             (0, OUT_H, FACE_W, OUT_H - FACE_W), (OUT_W, OUT_H, OUT_W - FACE_W, OUT_H - FACE_W)):
        d.line(x1, y1, x2, y2, "wood")
    # rabbet wall (dashed, on the back) and picture (dotted red)
    d.add(f'<rect class="hid" x="{d.x(WALL):.1f}" y="{d.y(WALL):.1f}" '
          f'width="{RAB_OPEN_W*S:.1f}" height="{RAB_OPEN_H*S:.1f}"/>')
    off = WALL + CLEAR
    d.add(f'<rect x="{d.x(off):.1f}" y="{d.y(off):.1f}" width="{PIC_W*S:.1f}" height="{PIC_H*S:.1f}" '
          f'fill="none" stroke="#b0452b" stroke-width="1.1" stroke-dasharray="2 3"/>')
    # piece names, centred in the bands (outside the hidden lines)
    cx, cy = OUT_W / 2, OUT_H / 2
    band = FACE_W * 0.42
    d.text(d.x(cx), d.y(band) + 4, f"rail · {frac(OUT_W)} long point", "n")
    d.text(d.x(cx), d.y(OUT_H - band) + 4, f"rail · {frac(OUT_W)} long point", "n")
    for xx in (band, OUT_W - band):
        d.add(f'<text class="n" transform="translate({d.x(xx)+4:.1f},{d.y(cy):.1f}) rotate(-90)" '
              f'text-anchor="middle">stile · {frac(OUT_H)} long point</text>')
    # legend in the opening
    d.text(d.x(cx), d.y(cy) - 22, f"sight opening {frac(SIGHT_W)} × {frac(SIGHT_H)}", "t")
    d.text(d.x(cx), d.y(cy) - 2, "dashed grey = rabbet wall (on the back)", "n")
    d.text(d.x(cx), d.y(cy) + 14, f"dotted red = picture / glass {frac(PIC_W)} × {frac(PIC_H)}", "n")
    d.text(d.x(cx), d.y(cy) + 36, "miter seams run corner to corner", "n")
    # dims: overall + rabbet on top, sight + rabbet on the right
    d.dim_h(0, OUT_W, 54, f"{frac(OUT_W)} overall (long points)", pyo=d.y(0))
    d.dim_h(WALL, OUT_W - WALL, 88, f"{frac(RAB_OPEN_W)} rabbet opening", pyo=d.y(0))
    d.dim_v(0, OUT_H, 52, f"{frac(OUT_H)} overall", pxo=d.x(0))
    d.dim_v(FACE_W, OUT_H - FACE_W, d.x(OUT_W) + 26, f"{frac(SIGHT_H)} sight",
            pxo=d.x(OUT_W), left=False)
    d.dim_v(WALL, OUT_H - WALL, d.x(OUT_W) + 62, f"{frac(RAB_OPEN_H)} rabbet opening",
            pxo=d.x(OUT_W) + 30, left=False)
    yb = d.y(OUT_H) + 28
    d.dim_h(0, FACE_W, yb, frac(FACE_W), pyo=d.y(OUT_H), below=True)
    d.dim_h(FACE_W, OUT_W - FACE_W, yb, f"{frac(SIGHT_W)} sight", pyo=d.y(OUT_H), below=True)
    d.dim_h(OUT_W - FACE_W, OUT_W, yb, frac(FACE_W), pyo=d.y(OUT_H), below=True)
    d.text(d.x(0), yb + 44, f"Frame = 2 rails (top/bottom) at {frac(OUT_W)} + 2 stiles (sides) at {frac(OUT_H)}, "
           "measured long point to long point.", "n", "start")
    d.text(d.x(0), yb + 60, f"Each piece: {frac(FACE_T)} thick × {frac(FACE_W)} wide, 45° miters, "
           f"{frac(RAB_W)} × {frac(RAB_D)} rabbet on the back inside edge.", "n", "start")
    d.save(path, "Picture frame, front elevation")


def profile(path):
    s = 160
    d = Drawing(780, 440, 150, 130, s=s)
    d.text(20, 24, "Profile section — 1 in = 160 px", "h", "start")
    x = d.x; y = d.y
    # stock: y=0 front face, y=FACE_T back; rabbet removed at inner (right) / back (bottom)
    d.poly([(0, 0), (FACE_W, 0), (FACE_W, LIP_T), (WALL, LIP_T), (WALL, FACE_T), (0, FACE_T)], "wood")
    gx0 = WALL + CLEAR
    gx1 = FACE_W + 0.6
    layers = [(f"glass {frac(GLASS_T)}", LIP_T, GLASS_T, "#cfe6f2"),
              (f"print ≤ {frac(PRINT_T)}", LIP_T + GLASS_T, PRINT_T, "#f4efe0"),
              (f"backing {frac(BACK_T)}", LIP_T + GLASS_T + PRINT_T, BACK_T, "#d9c3a0")]
    lx = x(gx1) + 40
    ly = [y(LIP_T) + 4, y(LIP_T) + 28, y(LIP_T) + 52, y(LIP_T) + 80]
    for (name, y0, th, col), yy in zip(layers, ly):
        d.add(f'<rect x="{x(gx0):.1f}" y="{y(y0):.1f}" width="{(gx1-gx0)*s:.1f}" height="{th*s:.1f}" '
              f'fill="{col}" stroke="#4a3320" stroke-width="1"/>')
        d.leader(x(gx1), y(y0 + th / 2), lx - 4, yy - 4, name)
    stack = GLASS_T + PRINT_T + BACK_T
    py0 = LIP_T + stack
    # flexi-point: a thin steel tab driven into the rabbet wall, bearing on the backing
    tab_t = 1 / 32
    d.add(f'<rect x="{x(WALL - 0.22):.1f}" y="{y(py0):.1f}" width="{(0.22 + CLEAR + 0.32)*s:.1f}" '
          f'height="{tab_t*s:.1f}" fill="#7a7a7a" stroke="#333" stroke-width="1"/>')
    d.leader(x(gx0 + 0.32), y(py0 + tab_t / 2), lx - 4, ly[3] - 4,
             f"flexi-point, driven into the wall ({frac(RAB_D - stack)} left)")
    d.text(x(FACE_W) + 16, y(0) + 4, "← FRONT face (viewer side)", "n", "start")
    # dims
    d.dim_h(0, FACE_W, 96, f"{frac(FACE_W)} wide", pyo=y(0))
    d.dim_v(0, FACE_T, 50, f"{frac(FACE_T)} tall", pxo=x(0))
    d.dim_v(0, LIP_T, 100, f"{frac(LIP_T)} lip", pxo=x(0))
    d.dim_v(LIP_T, FACE_T, 100, f"{frac(RAB_D)} deep", pxo=x(0))
    yb = y(FACE_T) + 24
    d.dim_h(0, WALL, yb, f"{frac(WALL)} wall", pyo=y(FACE_T), below=True)
    d.dim_h(WALL, FACE_W, yb, frac(RAB_W), pyo=y(FACE_T), below=True)
    d.text(x(WALL + RAB_W / 2), yb + 30, "rabbet width", "n")
    # glass-to-wall clearance: ext line drops from the stack edge through the open rabbet
    yc = yb + 52
    d.add(f'<line class="ext" x1="{x(gx0):.1f}" y1="{y(py0):.1f}" x2="{x(gx0):.1f}" y2="{yc+4:.1f}"/>')
    d.add(f'<line class="ext" x1="{x(WALL):.1f}" y1="{yb+4:.1f}" x2="{x(WALL):.1f}" y2="{yc+4:.1f}"/>')
    d.dim_h_small(WALL, gx0, yc, f"{frac(CLEAR)} clearance, glass edge to wall")
    d.text(x(0), yb + 30, "BACK (wall side) ↓", "n", "start")
    d.text(x(0), yb + 100, f"Rabbet is {frac(RAB_W)} wide × {frac(RAB_D)} deep. {frac(GLASS_T)} glass + print + "
           f"{frac(BACK_T)} backing ≈ {frac(stack)}, leaving ≈ {frac(RAB_D - stack)} for the points.", "n", "start")
    d.text(x(0), yb + 118, f"Glass edge sits {frac(CLEAR)} off the rabbet wall; the lip overlaps the picture by "
           f"{frac(RAB_W)} − {frac(CLEAR)} = {frac(RAB_W - CLEAR)} per side.", "n", "start")
    d.save(path, "Picture frame, profile section")


def nest_layout():
    """Alternate the miters along one stick: rail, stile, rail, stile.
    Returns [(name, lp, x_start, lp_on_bottom)], used length."""
    kh = KERF * math.sqrt(2)           # kerf measured along the stick on a 45° cut
    pieces = [("rail", OUT_W), ("stile", OUT_H), ("rail", OUT_W), ("stile", OUT_H)]
    out, x0 = [], 0.0
    for i, (name, lp) in enumerate(pieces):
        out.append((name, lp, x0, i % 2 == 0))
        x0 += lp - FACE_W + kh
    used = out[-1][2] + out[-1][1]
    return out, used


def parts(path):
    d = Drawing(720, 600, 90, 0, s=S)
    d.text(20, 24, "Parts, seen from the back — 1 in = 26 px", "h", "start")

    def piece(lp, top, title):
        # outer (long-point) edge on top, inner edge below; wall then rabbet floor
        d.text(20, top - 40, title, "t", "start")
        d.oy = top
        d.poly([(0, 0), (lp, 0), (lp - WALL, WALL), (WALL, WALL)], "wood")
        d.poly([(WALL, WALL), (lp - WALL, WALL), (lp - FACE_W, FACE_W), (FACE_W, FACE_W)], "shelf")
        d.dim_h(0, lp, top - 12, f"{frac(lp)} long point (outside edge)", pyo=top)
        d.dim_h(WALL, lp - WALL, d.y(FACE_W) + 22, f"{frac(lp - 2 * WALL)} at the rabbet wall",
                pyo=d.y(WALL), below=True)
        d.dim_h(FACE_W, lp - FACE_W, d.y(FACE_W) + 50, f"{frac(lp - 2 * FACE_W)} short point (= sight)",
                pyo=d.y(FACE_W), below=True)
        d.dim_v(0, FACE_W, d.x(0) - 22, frac(FACE_W), pxo=d.x(FACE_W))
        d.dim_v_text(WALL, FACE_W, d.x(lp) + 14, f"{frac(RAB_W)} rabbet floor, {frac(RAB_D)} down",
                     pxo=d.x(lp - FACE_W))
        d.text(d.x(lp / 2), d.y(WALL / 2) + 4, f"{frac(WALL)} wall", "n")

    piece(OUT_W, 92, f"Rail — cut 2 at {frac(OUT_W)}, 45° both ends (top and bottom)")
    piece(OUT_H, 262, f"Stile — cut 2 at {frac(OUT_H)}, 45° both ends (sides)")

    # stick layout at a smaller scale
    ks = 9
    sd = Drawing(720, 600, 30, 470, s=ks)
    sd.text(20, 430, "Cutting one 6′ stick — 1 in = 9 px (miters alternate so neighbours share a cut)", "t", "start")
    sd.rect(0, 0, STICK_L, FACE_W, "spacer")
    layout, used = nest_layout()
    for name, lp, x0, lp_bottom in layout:
        if lp_bottom:
            pts = [(x0, FACE_W), (x0 + lp, FACE_W), (x0 + lp - FACE_W, 0), (x0 + FACE_W, 0)]
        else:
            pts = [(x0, 0), (x0 + lp, 0), (x0 + lp - FACE_W, FACE_W), (x0 + FACE_W, FACE_W)]
        sd.poly(pts, "wood")
        sd.text(sd.x(x0 + lp / 2), sd.y(0) - 6, f"{name} {frac(lp)}", "n")
    sd.dim_h(0, used, sd.y(FACE_W) + 22, f"≈ {frac(round(used * 2) / 2)} used, with {len(layout) - 1} kerfs",
             pyo=sd.y(FACE_W), below=True)
    sd.dim_h(used, STICK_L, sd.y(FACE_W) + 22, f"≈ {frac(round((STICK_L - used) * 2) / 2)} left",
             pyo=sd.y(FACE_W), below=True)
    sd.text(20, 560, f"Four pieces = {frac(2 * OUT_W + 2 * OUT_H)} of long points; each shared cut saves "
            f"{frac(FACE_W)}, so the run is {frac(2 * OUT_W + 2 * OUT_H - 3 * FACE_W)} + kerfs. "
            "Keep the offcut for test miters.", "n", "start")
    d.p.extend(sd.p)
    d.save(path, "Picture frame, parts and stick layout")
    return used


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "..", "static", "static", "woodworking")
    os.makedirs(out, exist_ok=True)
    front(os.path.join(out, "picture-frame-front.svg"))
    profile(os.path.join(out, "picture-frame-profile.svg"))
    used = parts(os.path.join(out, "picture-frame-parts.svg"))
    print(f"stick: {used:.2f}″ used of {STICK_L:g}″, {STICK_L - used:.2f}″ left")
    print("wrote 3 SVGs to", os.path.normpath(out))
