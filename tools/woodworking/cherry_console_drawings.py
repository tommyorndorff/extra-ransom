#!/usr/bin/env python3
"""True-scale SVGs for the Cherry Hallway Console plan (+ a drawbore detail).

Usage: python3 tools/woodworking/cherry_console_drawings.py
Writes static/static/woodworking/cherry-console-{front,side,plan,drawbore}.svg
Geometry in inches. Reuses the Drawing helper from modern_craftsman_drawings.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from modern_craftsman_drawings import Drawing, S

W, D, H = 42, 14, 34         # overall
OV = 1                        # top overhang all round
TOP_T, LEG = 0.75, 1.5
AP_H, RAIL_H = 3.5, 2.5       # apron / lower rail heights (both 3/4 thick)
RAIL_TOP = 9.25               # rail top above floor; shelf (3/4) sits on it -> top at 10"
SHELF_T = 0.75
FR_W, FR_D = W - 2 * OV, D - 2 * OV   # 40 x 12
L0, L1 = OV, OV + LEG                  # left leg x 1..2.5
R0, R1 = W - OV - LEG, W - OV          # right leg x 39.5..41
F0, F1 = OV, OV + LEG                  # front leg depth 1..2.5
B0, B1 = D - OV - LEG, D - OV          # back leg depth 11.5..13


def front(path):
    d = Drawing(730, 590, 95, 100)
    d.text(20, 24, "Front elevation — 1 in = 12 px", "h", "start")
    sy = H - RAIL_TOP - SHELF_T
    d.rect(L1, sy, R0, sy + SHELF_T, "shelf")
    d.rect(0, 0, W, TOP_T, "wood")
    d.rect(L0, TOP_T, L1, H, "leg")
    d.rect(R0, TOP_T, R1, H, "leg")
    d.rect(L1, TOP_T, R0, TOP_T + AP_H, "face")
    ry = H - RAIL_TOP
    d.rect(L1, ry, R0, ry + RAIL_H, "face")
    d.add(f'<line class="floor" x1="{d.x(-3):.1f}" y1="{d.y(H):.1f}" x2="{d.x(W+3):.1f}" y2="{d.y(H):.1f}"/>')
    d.text(d.x(21), d.y(TOP_T + AP_H / 2) + 4, "front apron ¾″ × 3½″", "n")
    d.text(d.x(21), d.y(ry + RAIL_H / 2) + 4, "lower rail ¾″ × 2½″", "n")
    d.text(d.x(21), d.y(sy) - 6, "shelf ¾″ (rests on rails)", "n")
    d.dim_h(0, W, 42, "42″ overall", pyo=d.y(0))
    d.dim_h(0, OV, 68, "1″", pyo=d.y(0))
    d.dim_h(OV, W - OV, 68, "40″ leg frame", pyo=d.y(TOP_T))
    d.dim_h(W - OV, W, 68, "1″", pyo=d.y(0))
    d.dim_v(0, H, 52, "34″ overall", pxo=d.x(0))
    px = d.x(W) + 24
    d.dim_v(TOP_T, TOP_T + AP_H, px, "3½″ apron", pxo=d.x(W))
    d.dim_v(ry, ry + RAIL_H, px, "2½″ rail", pxo=d.x(R1))
    d.dim_v(H - RAIL_TOP - SHELF_T, H, px + 56, "shelf top ≈ 10″ off floor", pxo=d.x(R1))
    yb = d.y(H) + 28
    d.dim_h(L0, L1, yb, "1½″", pyo=d.y(H), below=True)
    d.dim_h(L1, R0, yb, "37″ shoulder to shoulder (tenons add 1″ each end = 39″ cut)", pyo=d.y(H), below=True)
    d.dim_h(R0, R1, yb, "1½″", pyo=d.y(H), below=True)
    d.save(path, "Cherry hallway console, front elevation")


def side(path):
    d = Drawing(540, 590, 95, 100)
    d.text(20, 24, "Side elevation — 1 in = 12 px", "h", "start")
    sy = H - RAIL_TOP - SHELF_T
    d.rect(F1, sy, B0, sy + SHELF_T, "shelf")
    d.rect(0, 0, D, TOP_T, "wood")
    d.rect(F0, TOP_T, F1, H, "leg")
    d.rect(B0, TOP_T, B1, H, "leg")
    d.rect(F1, TOP_T, B0, TOP_T + AP_H, "face")
    ry = H - RAIL_TOP
    d.rect(F1, ry, B0, ry + RAIL_H, "face")
    d.add(f'<line class="floor" x1="{d.x(-3):.1f}" y1="{d.y(H):.1f}" x2="{d.x(D+3):.1f}" y2="{d.y(H):.1f}"/>')
    d.text(d.x(7), d.y(TOP_T + AP_H / 2) + 4, "side apron", "n")
    d.text(d.x(7), d.y(ry + RAIL_H / 2) + 4, "lower rail", "n")
    d.text(d.x(0.5), d.y(H) - 8, "front", "n", "start")
    d.dim_h(0, D, 42, "14″ overall", pyo=d.y(0))
    d.dim_h(0, OV, 68, "1″", pyo=d.y(0))
    d.dim_h(OV, D - OV, 68, "12″ leg frame", pyo=d.y(TOP_T))
    d.dim_h(D - OV, D, 68, "1″", pyo=d.y(0))
    d.dim_v(0, H, 52, "34″ overall", pxo=d.x(0))
    d.dim_v(H - RAIL_TOP - SHELF_T, H, d.x(D) + 30, "shelf top ≈ 10″", pxo=d.x(B1), left=False)
    yb = d.y(H) + 28
    d.dim_h(F0, F1, yb, "1½″", pyo=d.y(H), below=True)
    d.dim_h(F1, B0, yb, "9″ shoulders", pyo=d.y(H), below=True)
    d.dim_h(B0, B1, yb, "1½″", pyo=d.y(H), below=True)
    d.save(path, "Cherry hallway console, side elevation")


def plan(path):
    oy = 100
    d = Drawing(760, 390, 95, oy)
    Y = lambda dep: oy + (D - dep) * S
    X = d.x
    def prect(x1, a, x2, b, cls):
        d.add(f'<rect class="{cls}" x="{X(x1):.2f}" y="{Y(b):.2f}" width="{(x2-x1)*S:.2f}" height="{(b-a)*S:.2f}"/>')
    d.text(20, 24, "Plan view, top removed — 1 in = 12 px", "h", "start")
    d.add(f'<rect class="hid" x="{X(0):.1f}" y="{Y(D):.1f}" width="{W*S}" height="{D*S}"/>')
    # shelf, notched around legs
    pts = [(L1, F0), (R0, F0), (R0, F1), (R1, F1), (R1, B0), (R0, B0), (R0, B1), (L1, B1),
           (L1, B0), (L0, B0), (L0, F1), (L1, F1)]
    d.add('<polygon class="shelf" points="' + ' '.join(f'{X(x):.1f},{Y(dep):.1f}' for x, dep in pts) + '"/>')
    d.text(X(W / 2), Y(7) + 4, "shelf ¾″ × 12″ × 40″ (corners notched 1½″ × 1½″)", "n")
    # aprons (flush outside) over the shelf edge
    prect(L1, F0, R0, F0 + 0.75, "wood"); prect(L1, B1 - 0.75, R0, B1, "wood")
    prect(L0, F1, L0 + 0.75, B0, "wood"); prect(R1 - 0.75, F1, R1, B0, "wood")
    for x in (L0, R0):
        prect(x, F0, x + LEG, F1, "leg"); prect(x, B0, x + LEG, B1, "leg")
    d.text(X(W / 2), Y(0) + 16, "FRONT", "n")
    d.text(X(0), Y(0) + 62, "Dashed outline = top, 42″ × 14″ × ¾″, floating on buttons or figure-8s.  Aprons and lower rails are ¾″ thick, flush to the leg outer faces;", "n", "start")
    d.text(X(0), Y(0) + 78, "the lower rails lie directly under the shelf edges. Tenons (1″ long, 5/16″ thick) are not shown.", "n", "start")
    d.dim_h(0, W, 42, "42″ overall", pyo=Y(D))
    d.dim_h(0, OV, 68, "1″", pyo=Y(D))
    d.dim_h(OV, W - OV, 68, "40″ leg frame", pyo=Y(B1))
    d.dim_h(W - OV, W, 68, "1″", pyo=Y(D))
    yb = Y(0) + 34
    d.dim_h(L1, R0, yb, "37″ shoulder to shoulder", pyo=Y(F0), below=True)
    def dim_depth(a, b, px, label):
        ya, yb2 = Y(a), Y(b)
        d.add(f'<line class="dim" x1="{px}" y1="{ya:.1f}" x2="{px}" y2="{yb2:.1f}" marker-start="url(#a)" marker-end="url(#a)"/>')
        d.add(f'<text class="t" transform="translate({px+14},{(ya+yb2)/2:.1f}) rotate(-90)" text-anchor="middle">{label}</text>')
    dim_depth(0, D, X(W) + 24, "14″ overall")
    dim_depth(OV, D - OV, X(W) + 54, "12″ leg frame")
    dim_depth(F1, B0, X(0) - 24, "9″ shoulders")
    d.save(path, "Cherry hallway console, plan view")


def drawbore(path):
    P = 200
    d = Drawing(780, 600, 330, 120, s=P)
    d.text(20, 24, "Drawbore detail — section through the pin axis, 1 in = 200 px (offset is true to scale)", "h", "start")
    x, y = d.x, d.y
    pin_x, off = 0.5, 1 / 32
    my1, my2 = 0.375, 0.6875            # mortise / tenon faces in the section (5/16″ wide)
    d.rect(0, 0, 1.5, 1.5, "leg")                       # leg
    d.rect(-1.6, my1 - 0.21875, 0, my2 + 0.21875, "face")   # apron (3/4″ thick, set back from outer face)
    d.rect(0, my1, 1.0, my2, "face")                     # tenon in its mortise
    # leg hole (blue): from the outer face (y=0), through near wall + mortise, 1/4″ into far wall
    d.add(f'<rect x="{x(pin_x-0.0625):.1f}" y="{y(0):.1f}" width="{0.125*P:.1f}" height="{0.9375*P:.1f}" fill="#fff" stroke="#1f5fa8" stroke-width="1.4" fill-opacity=".92"/>')
    # tenon hole (red): same size, centre 1/32″ closer to the shoulder
    d.add(f'<rect x="{x(pin_x-off-0.0625):.1f}" y="{y(my1):.1f}" width="{0.125*P:.1f}" height="{(my2-my1)*P:.1f}" fill="#fff" stroke="#c0392b" stroke-width="1.6" fill-opacity=".92"/>')
    # centre lines + labels
    d.add(f'<line x1="{x(pin_x):.1f}" y1="{y(-0.3):.1f}" x2="{x(pin_x):.1f}" y2="{y(0):.1f}" stroke="#1f5fa8" stroke-width="1.4"/>')
    d.add(f'<line x1="{x(pin_x-off):.1f}" y1="{y(-0.3):.1f}" x2="{x(pin_x-off):.1f}" y2="{y(my1):.1f}" stroke="#c0392b" stroke-width="1.4" stroke-dasharray="4 3"/>')
    d.text(x(pin_x) + 8, y(-0.2), "hole in leg (drill first)", "t", "start")
    d.text(x(pin_x - off) - 8, y(-0.2), "hole in tenon, 1/32″ nearer the shoulder", "t", "end")
    d.text(x(pin_x), y(-0.36), "pin Ø 1/8″, ½″ from shoulder", "n")
    d.text(x(0.64), y(0.1), "outer face (pin enters)", "n", "start")
    d.text(x(0.75), y(1.5) - 6, "far wall: hole stops ¼″ in (blind)", "n")
    d.text(x(-0.8), y(0.53) + 4, "apron ¾″", "n")
    d.text(x(-0.05), y(0.1), "shoulder at leg face", "n", "end")
    d.dim_h(0, 1.0, y(1.5) + 32, "tenon 1″ long", pyo=y(0.6875), below=True)
    d.dim_h(0, pin_x, y(1.5) + 62, "½″", pyo=y(1.0), below=True)
    d.dim_v(my1, my2, x(1.5) + 36, "5/16″ mortise = tenon thickness", pxo=x(1.0), left=False)
    d.save(path, "Drawbore detail")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "..", "static", "static", "woodworking")
    os.makedirs(out, exist_ok=True)
    front(os.path.join(out, "cherry-console-front.svg"))
    side(os.path.join(out, "cherry-console-side.svg"))
    plan(os.path.join(out, "cherry-console-plan.svg"))
    drawbore(os.path.join(out, "cherry-console-drawbore.svg"))
    print("wrote 4 SVGs to", os.path.normpath(out))
