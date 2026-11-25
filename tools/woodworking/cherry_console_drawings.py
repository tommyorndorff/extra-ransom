#!/usr/bin/env python3
"""True-scale SVGs for the Cherry Hallway Console plan (+ drawbore and leg-layout details).

Usage: python3 tools/woodworking/cherry_console_drawings.py
Writes public/static/woodworking/cherry-console-{front,side,plan,drawbore,legs}.svg
Geometry in inches. Reuses the Drawing helper from modern_craftsman_drawings.py.
Every label is built from the constants below with frac(), so edit them and re-run.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from modern_craftsman_drawings import Drawing, S, frac

W, D, H = 42, 14, 34         # overall
OV = 1                        # top overhang all round
TOP_T, LEG = 0.75, 1.5
AP_H, RAIL_H = 3.5, 2.5       # apron / lower rail heights
STOCK_T = 0.75                # aprons and rails are 3/4 thick, flush to the leg outer faces
RAIL_TOP = 9.25               # rail top above floor; shelf (3/4) sits on it -> top at 10"
SHELF_T = 0.75
FR_W, FR_D = W - 2 * OV, D - 2 * OV   # 40 x 12 leg frame (= shelf size)
L0, L1 = OV, OV + LEG                  # left leg x 1..2.5
R0, R1 = W - OV - LEG, W - OV          # right leg x 39.5..41
F0, F1 = OV, OV + LEG                  # front leg depth 1..2.5
B0, B1 = D - OV - LEG, D - OV          # back leg depth 11.5..13
LEG_L = H - TOP_T                      # 33 1/4 leg length
TEN = 1.0                              # tenon length
SH_L, SH_S = FR_W - 2 * LEG, FR_D - 2 * LEG   # 37 / 9 shoulder to shoulder
CUT_L, CUT_S = SH_L + 2 * TEN, SH_S + 2 * TEN # 39 / 11 cut lengths
TEN_T = 5 / 16                         # tenon / mortise thickness
NEAR = (STOCK_T - TEN_T) / 2           # 7/32 leg face to mortise (tenon centred on the stock)
PIN_D, PIN_IN, OFF, BLIND = 1 / 8, 0.5, 1 / 32, 0.25
PINS_LONG, PIN_SHORT = (0.75, 2.75), 1.75     # pin heights below the leg/apron top
RAIL_ZONE = (LEG_L - RAIL_TOP, LEG_L - RAIL_TOP + RAIL_H)   # 24..26 1/2 below leg top

EXTRA = """
<style>
  .mort{fill:#6b4a2e;fill-opacity:.28;stroke:#4a3320;stroke-width:1;stroke-dasharray:4 2}
  .slot{fill:#6b4a2e;stroke:none}
  .pinh{fill:#fff;stroke:#1f5fa8;stroke-width:1.4}
  .pinl{stroke:#1f5fa8;stroke-width:2}
  .brk{fill:none;stroke:#4a3320;stroke-width:1.2}
  .ts{font:600 12px 'Helvetica Neue',Arial,sans-serif;fill:#1f3a5f}
</style>
"""


def frac32(v):
    """frac() to the nearest 1/32″ (frac() itself stops at 1/16″)."""
    n = round(v * 32)
    if n % 2 == 0:
        return frac(n / 32)
    whole, rem = divmod(n, 32)
    return (f"{whole} " if whole else "") + f"{rem}/32″"


class CDrawing(Drawing):
    """Local additions (the shared helper is frozen)."""

    def rtext(self, px, py, s, cls="n"):
        """Text rotated to read bottom-to-top, centred on (px, py) in pixels."""
        self.add(f'<text class="{cls}" transform="translate({px + 4:.1f},{py:.1f}) rotate(-90)" '
                 f'text-anchor="middle">{s}</text>')

    def overhang_row(self, total, row, frame_label, pyo_edge, pyo_frame):
        """1″ | frame | 1″ chain with the tiny 1″ labels set outside the ends."""
        self.dim_h(0, OV, row, "", pyo=pyo_edge)
        self.dim_h(OV, total - OV, row, frame_label, pyo=pyo_frame)
        self.dim_h(total - OV, total, row, "", pyo=pyo_edge)
        self.text(self.x(0) - 5, row + 4, frac(OV), "t", "end")
        self.text(self.x(total) + 5, row + 4, frac(OV), "t", "start")

    def dim_v_small(self, y1, y2, px, label, pxo=None, lx=None, ly=None, anchor="middle"):
        """Vertical dim for a span too short for inside arrows: arrows outside, pointing in."""
        a, b = self.y(y1), self.y(y2)
        if pxo is not None:
            for yy in (a, b):
                self.add(f'<line class="ext" x1="{px:.1f}" y1="{yy:.1f}" x2="{pxo:.1f}" y2="{yy:.1f}"/>')
        self.add(f'<line class="dim" x1="{px:.1f}" y1="{a-14:.1f}" x2="{px:.1f}" y2="{a:.1f}" marker-end="url(#a)"/>')
        self.add(f'<line class="dim" x1="{px:.1f}" y1="{b+14:.1f}" x2="{px:.1f}" y2="{b:.1f}" marker-end="url(#a)"/>')
        self.text(px if lx is None else lx, a - 18 if ly is None else ly, label, "t", anchor)

    def floor(self, x1, x2):
        self.add(f'<line class="floor" x1="{self.x(x1):.1f}" y1="{self.y(H):.1f}" '
                 f'x2="{self.x(x2):.1f}" y2="{self.y(H):.1f}"/>')


def front(path):
    d = CDrawing(760, 580, 95, 100)
    d.text(20, 24, "Front elevation — 1 in = 12 px", "h", "start")
    sy = H - RAIL_TOP - SHELF_T
    ry = H - RAIL_TOP
    d.rect(L1, sy, R0, sy + SHELF_T, "shelf")
    d.rect(0, 0, W, TOP_T, "wood")
    d.rect(L0, TOP_T, L1, H, "leg")
    d.rect(R0, TOP_T, R1, H, "leg")
    d.rect(L1, TOP_T, R0, TOP_T + AP_H, "face")
    d.rect(L1, ry, R0, ry + RAIL_H, "face")
    d.floor(-3, W + 3)
    d.text(d.x(W / 2), d.y(TOP_T + AP_H / 2) + 4, f"front apron {frac(STOCK_T)} × {frac(AP_H)}", "n")
    d.text(d.x(W / 2), d.y(ry + RAIL_H / 2) + 4, f"lower rail {frac(STOCK_T)} × {frac(RAIL_H)}", "n")
    d.text(d.x(W / 2), d.y(sy) - 6, f"shelf {frac(SHELF_T)} (rests on the rails)", "n")
    # top
    d.dim_h(0, W, 42, f"{frac(W)} overall", pyo=d.y(0))
    d.overhang_row(W, 68, f"{frac(FR_W)} leg frame", d.y(0), d.y(TOP_T))
    # left
    d.dim_v(0, H, 52, f"{frac(H)} overall", pxo=d.x(0))
    d.dim_v(TOP_T, H, 78, f"{frac(LEG_L)} leg", pxo=d.x(L0))
    # right: top + apron chain, rail, then rail-top and shelf-top heights off the floor
    c1 = d.x(W) + 18
    d.dim_v_small(0, TOP_T, c1, f"{frac(TOP_T)} top", pxo=d.x(W), lx=c1 + 6, ly=d.y(0) - 4, anchor="start")
    d.dim_v_text(TOP_T, TOP_T + AP_H, c1, f"{frac(AP_H)} apron", pxo=d.x(R0))
    d.dim_v_text(ry, ry + RAIL_H, c1, f"{frac(RAIL_H)} rail", pxo=d.x(R0))
    d.dim_v(ry, H, c1 + 72, f"{frac(RAIL_TOP)} floor to rail top", pxo=d.x(R0), left=False)
    d.dim_v(sy, H, c1 + 104, f"{frac(RAIL_TOP + SHELF_T)} floor to shelf top", pxo=d.x(R0), left=False)
    # bottom
    yb = d.y(H) + 28
    d.dim_h(L0, L1, yb, frac(LEG), pyo=d.y(H), below=True)
    d.dim_h(L1, R0, yb, f"{frac(SH_L)} shoulder to shoulder (+ {frac(TEN)} tenon each end = {frac(CUT_L)} cut)",
            pyo=d.y(H), below=True)
    d.dim_h(R0, R1, yb, frac(LEG), pyo=d.y(H), below=True)
    d.save(path, "Cherry hallway console, front elevation")


def side(path):
    d = CDrawing(420, 580, 95, 100)
    d.text(20, 24, "Side elevation — 1 in = 12 px", "h", "start")
    sy = H - RAIL_TOP - SHELF_T
    ry = H - RAIL_TOP
    d.rect(F1, sy, B0, sy + SHELF_T, "shelf")
    d.rect(0, 0, D, TOP_T, "wood")
    d.rect(F0, TOP_T, F1, H, "leg")
    d.rect(B0, TOP_T, B1, H, "leg")
    d.rect(F1, TOP_T, B0, TOP_T + AP_H, "face")
    d.rect(F1, ry, B0, ry + RAIL_H, "face")
    d.floor(-3, D + 3)
    d.text(d.x(D / 2), d.y(TOP_T + AP_H / 2) - 2, "side apron", "n")
    d.text(d.x(D / 2), d.y(TOP_T + AP_H / 2) + 12, f"{frac(STOCK_T)} × {frac(AP_H)}", "n")
    d.text(d.x(D / 2), d.y(ry) + 12, "side rail", "n")
    d.text(d.x(D / 2), d.y(ry) + 25, f"{frac(STOCK_T)} × {frac(RAIL_H)}", "n")
    d.text(d.x(F0) - 5, d.y(H) - 8, "front", "n", "end")
    d.text(d.x(B1) + 5, d.y(H) - 8, "back", "n", "start")
    d.dim_h(0, D, 42, f"{frac(D)} overall", pyo=d.y(0))
    d.overhang_row(D, 68, f"{frac(FR_D)} leg frame", d.y(0), d.y(TOP_T))
    d.dim_v(0, H, 52, f"{frac(H)} overall", pxo=d.x(0))
    d.dim_v(sy, H, d.x(D) + 30, f"{frac(RAIL_TOP + SHELF_T)} floor to shelf top", pxo=d.x(B0), left=False)
    yb = d.y(H) + 28
    d.dim_h(F0, F1, yb, frac(LEG), pyo=d.y(H), below=True)
    d.dim_h(F1, B0, yb, f"{frac(SH_S)} shoulders", pyo=d.y(H), below=True)
    d.dim_h(B0, B1, yb, frac(LEG), pyo=d.y(H), below=True)
    d.text(d.x(D / 2), yb + 34, f"cut {frac(CUT_S)} with {frac(TEN)} tenons", "n")
    d.save(path, "Cherry hallway console, side elevation")


def plan(path):
    oy = 100
    d = CDrawing(760, 400, 95, oy)
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
    d.text(X(W / 2), Y(D / 2) + 4,
           f"shelf {frac(SHELF_T)} × {frac(FR_D)} × {frac(FR_W)} (corners notched {frac(LEG)} × {frac(LEG)})", "n")
    # aprons (flush outside) over the shelf edge
    prect(L1, F0, R0, F0 + STOCK_T, "wood"); prect(L1, B1 - STOCK_T, R0, B1, "wood")
    prect(L0, F1, L0 + STOCK_T, B0, "wood"); prect(R1 - STOCK_T, F1, R1, B0, "wood")
    for x in (L0, R0):
        prect(x, F0, x + LEG, F1, "leg"); prect(x, B0, x + LEG, B1, "leg")
    d.text(X(W / 2), Y(0) + 16, "FRONT", "n")
    d.dim_h(0, W, 42, f"{frac(W)} overall", pyo=Y(D))
    d.overhang_row(W, 68, f"{frac(FR_W)} leg frame", Y(D), Y(B1))
    yb = Y(0) + 34
    d.dim_h(L1, R0, yb, f"{frac(SH_L)} shoulder to shoulder", pyo=Y(F0), below=True)
    def dim_depth(a, b, px, label, pxo, right=True):
        ya, yb2 = Y(a), Y(b)
        for yy in (ya, yb2):
            d.add(f'<line class="ext" x1="{px:.1f}" y1="{yy:.1f}" x2="{pxo:.1f}" y2="{yy:.1f}"/>')
        d.add(f'<line class="dim" x1="{px}" y1="{ya:.1f}" x2="{px}" y2="{yb2:.1f}" marker-start="url(#a)" marker-end="url(#a)"/>')
        tx = px + 14 if right else px - 6
        d.add(f'<text class="t" transform="translate({tx},{(ya+yb2)/2:.1f}) rotate(-90)" text-anchor="middle">{label}</text>')
    dim_depth(OV, D - OV, X(W) + 24, f"{frac(FR_D)} leg frame", X(R1))
    dim_depth(0, D, X(W) + 54, f"{frac(D)} overall", X(W))
    dim_depth(F1, B0, X(0) - 24, f"{frac(SH_S)} shoulders", X(L0))
    notes = [f"Dashed outline = top, {frac(W)} × {frac(D)} × {frac(TOP_T)}, floating on buttons or figure-8s.",
             f"Aprons and lower rails are {frac(STOCK_T)} thick, flush to the leg outer faces; the lower rails lie directly under",
             f"the shelf edges. Tenons ({frac(TEN)} long, {frac(TEN_T)} thick, tips mitred) are not shown — see the leg layout."]
    for i, s in enumerate(notes):
        d.text(X(0), Y(0) + 70 + 16 * i, s, "n", "start")
    d.save(path, "Cherry hallway console, plan view")


def drawbore(path):
    P = 200
    d = CDrawing(820, 700, 310, 175, s=P)
    d.text(20, 24, f"Drawbore detail — section looking down through a front-apron pin, 1 in = {P} px (true scale)", "h", "start")
    x, y = d.x, d.y
    my1, my2 = NEAR, NEAR + TEN_T            # tenon cheeks, measured in from the outer (front) face
    hole_end = my2 + BLIND
    sx1, sx2 = LEG - my2, LEG - my1          # side-apron tenon, measured in from the end face
    # front apron (flush with the leg's front face) and the side apron leaving the back face
    AL, SL = 1.25, 0.8                       # lengths of the apron stubs shown
    zl = 6 / P                               # break-line zigzag amplitude, in inches
    d.poly([(-AL, 0), (0, 0), (0, STOCK_T), (-AL, STOCK_T), (-AL + zl, 0.56), (-AL - zl, 0.375), (-AL + zl, 0.19)], "face")
    d.poly([(LEG - STOCK_T, LEG), (LEG, LEG), (LEG, LEG + SL), (LEG - 0.19, LEG + SL + zl),
            (LEG - 0.375, LEG + SL - zl), (LEG - 0.56, LEG + SL + zl), (LEG - STOCK_T, LEG + SL)], "face")
    d.rect(0, 0, LEG, LEG, "leg")
    # the two tenons, tips mitred on the leg diagonal (outer corner to inner corner)
    d.poly([(0, my1), (TEN, my1), (TEN, LEG - TEN), (LEG - my2, my2), (0, my2)], "face")
    d.poly([(sx1, LEG), (sx2, LEG), (sx2, LEG - TEN), (TEN, LEG - TEN), (sx1, LEG - sx1)], "face")
    pin_x = PIN_IN
    r = PIN_D / 2
    # leg hole (blue): from the outer face, through the near wall + mortise, BLIND into the far wall
    d.add(f'<rect x="{x(pin_x-r):.1f}" y="{y(0):.1f}" width="{PIN_D*P:.1f}" height="{hole_end*P:.1f}" fill="#fff" stroke="#1f5fa8" stroke-width="1.4" fill-opacity=".92"/>')
    # tenon hole (red): same size, centre OFF closer to the shoulder
    d.add(f'<rect x="{x(pin_x-OFF-r):.1f}" y="{y(my1):.1f}" width="{PIN_D*P:.1f}" height="{TEN_T*P:.1f}" fill="#fff" stroke="#c0392b" stroke-width="1.6" fill-opacity=".92"/>')
    # centre lines + labels
    top = 78
    d.add(f'<line x1="{x(pin_x):.1f}" y1="{top}" x2="{x(pin_x):.1f}" y2="{y(0):.1f}" stroke="#1f5fa8" stroke-width="1.4"/>')
    d.add(f'<line x1="{x(pin_x-OFF):.1f}" y1="{top}" x2="{x(pin_x-OFF):.1f}" y2="{y(my1):.1f}" stroke="#c0392b" stroke-width="1.4" stroke-dasharray="4 3"/>')
    d.text(x(pin_x), 66, f"pin Ø {frac(PIN_D)}, {frac(PIN_IN)} from the shoulder", "n")
    d.text(x(pin_x) + 8, 94, "hole in leg (drill first)", "t", "start")
    d.text(x(pin_x - OFF) - 8, 94, f"hole in tenon, {frac32(OFF)} nearer the shoulder", "t", "end")
    # dims above the leg, measured from the shoulder
    d.dim_h(0, TEN, y(0) - 52, "", pyo=y(0))
    d.text(x(0.8), y(0) - 57, f"tenon {frac(TEN)} long", "t")
    d.add(f'<line class="ext" x1="{x(TEN):.1f}" y1="{y(0):.1f}" x2="{x(TEN):.1f}" y2="{y(my1):.1f}"/>')
    d.dim_h(0, pin_x, y(0) - 26, frac(PIN_IN), pyo=y(0))
    d.text(x(0) - 6, y(0) - 8, "shoulder (leg face)", "n", "end")
    # mortise / hole-depth chain at the right
    c = x(LEG) + 30
    d.dim_v_text(0, my1, c, f"{frac32(NEAR)} near wall")
    d.add(f'<line class="ext" x1="{c:.1f}" y1="{y(0):.1f}" x2="{x(LEG):.1f}" y2="{y(0):.1f}"/>')
    d.dim_v_text(my1, my2, c, f"{frac(TEN_T)} mortise (= tenon)", pxo=x(TEN))
    d.dim_v_text(my2, hole_end, c, f"{frac(BLIND)} into the far wall (blind)", pxo=x(pin_x + r))
    # labels inside parts
    d.text(x((TEN + LEG) / 2), y(0) + 15, "outer face", "n")
    d.text(x((TEN + LEG) / 2), y(0) + 28, "pin enters", "n")
    d.text(x(-AL / 2), y(STOCK_T / 2) - 2, f"front apron {frac(STOCK_T)}", "n")
    d.text(x(-AL / 2), y(STOCK_T / 2) + 12, "flush with the leg", "n")
    d.text(x(0.22), y((my1 + my2) / 2) + 4, "tenon", "n")
    d.rtext(x((sx1 + sx2) / 2), y(1.05), "side-apron tenon")
    d.text(x(LEG - STOCK_T / 2), y(LEG + SL / 2) - 2, "side apron", "n")
    d.text(x(LEG - STOCK_T / 2), y(LEG + SL / 2) + 12, frac(STOCK_T), "n")
    d.leader(x((TEN + LEG - my2) / 2), y((LEG - TEN + my2) / 2), x(0.88), y(0.95),
             "tips mitred 45°", "end")
    d.text(x(0.88) - 3, y(0.95) + 18, "where the tenons meet", "n", "end")
    notes = [f"Tenons are centred on the {frac(STOCK_T)} aprons, which are flush with the leg faces, so the near wall is {frac32(NEAR)}.",
             f"The side-apron pin is drilled from the end face at {frac(PIN_SHORT)} below the top, between the front-apron pins",
             f"at {frac(PINS_LONG[0])} and {frac(PINS_LONG[1])}, so it is not in this section. See the leg layout for all pin positions."]
    for i, s in enumerate(notes):
        d.text(20, 652 + 16 * i, s, "n", "start")
    d.save(path, "Drawbore detail", extra=EXTRA)


def legs(path):
    """Leg layout for the front-left leg: full-length mortised faces + the top 4″ unfolded."""
    d = CDrawing(820, 610, 130, 96)               # left panel, 1 in = 12 px
    d.text(20, 24, "Leg layout — front-left leg (2 as drawn, 2 mirrored)", "h", "start")
    d.text(20, 54, f"Mortised faces, full length — 1 in = {S} px", "ts", "start")
    x, y = d.x, d.y
    NL = NEAR + TEN_T
    d.rect(0, 0, LEG, LEG_L, "leg")
    d.rect(LEG, 0, 2 * LEG, LEG_L, "leg")
    for v0, v1 in ((0, AP_H), RAIL_ZONE):
        d.rect(NEAR, v0, NL, v1, "slot")                       # inner face: near its front edge (B)
        d.rect(2 * LEG - NL, v0, 2 * LEG - NEAR, v1, "slot")   # back face: near its end edge (D)
    d.rtext(x(LEG / 2) + 1, y(14), "inner face")
    d.rtext(x(1.5 * LEG) + 1, y(14), "back face")
    for u, s in ((0, "B"), (LEG, "C"), (2 * LEG, "D")):
        d.text(x(u), y(LEG_L) + 16, s, "ts")
    d.text(x(LEG), y(0) - 8, "top", "n")
    # left: chain from the top, cumulative to the rail, overall
    z0, z1 = RAIL_ZONE
    for a, b in ((0, AP_H), (AP_H, z0), (z0, z1), (z1, LEG_L)):
        d.dim_v(a, b, x(0) - 24, frac(b - a), pxo=x(0))
    d.dim_v(0, z0, x(0) - 50, f"{frac(z0)} top to rail mortise", pxo=x(0))
    d.dim_v(0, LEG_L, x(0) - 76, f"{frac(LEG_L)} leg", pxo=x(0))
    d.leader(x(2 * LEG), y(AP_H / 2), x(2 * LEG) + 22, y(AP_H / 2), "apron mortises", "start")
    d.leader(x(2 * LEG), y((z0 + z1) / 2), x(2 * LEG) + 22, y((z0 + z1) / 2), "rail mortises", "start")
    d.text(x(2 * LEG) + 25, y((z0 + z1) / 2) + 18, f"{frac(z0)}–{frac(z1)} below the top", "n", "start")

    # right panel: top 4″ of all four faces, unfolded, 1 in = 48 px
    K = 48
    r = CDrawing(1, 1, 440, 130, s=K)
    X, Yr = r.x, r.y
    VIS = 4.0
    r.text(400, 54, f"Top {frac(VIS)} of the leg, all four faces unfolded (seen from outside) — 1 in = {K} px", "ts", "start")
    faces = [("front", "outer"), ("inner", "mortised"), ("back", "mortised"), ("end", "outer")]
    for i, (t1, t2) in enumerate(faces):
        u0 = i * LEG
        pts = [(u0, 0), (u0 + LEG, 0)] + [(u0 + LEG - LEG * k / 4, VIS + (0.06 if k % 2 else -0.06)) for k in range(5)]
        r.poly(pts, "leg")
        r.text(X(u0 + LEG / 2), Yr(0) - 30, t1, "ts")
        r.text(X(u0 + LEG / 2), Yr(0) - 16, t2, "n")
    for i, s in enumerate("ABCDA"):
        r.text(X(i * LEG), Yr(0) - 4, s, "ts")
    # mortises (apron zone): inner face near B, back face near D
    r.rect(LEG + NEAR, 0, LEG + NL, AP_H, "mort")
    r.rect(3 * LEG - NL, 0, 3 * LEG - NEAR, AP_H, "mort")
    r.rtext(X(LEG + 1.0), Yr(AP_H / 2), "front-apron mortise")
    r.rtext(X(2 * LEG + 0.5), Yr(AP_H / 2), "side-apron mortise")
    # pins: front face ½″ from B (the front-apron shoulder face), end face ½″ from D
    pf_u, pe_u = LEG - PIN_IN, 3 * LEG + PIN_IN
    for v in PINS_LONG:
        r.add(f'<circle class="pinh" cx="{X(pf_u):.1f}" cy="{Yr(v):.1f}" r="{PIN_D / 2 * K:.1f}"/>')
    r.add(f'<circle class="pinh" cx="{X(pe_u):.1f}" cy="{Yr(PIN_SHORT):.1f}" r="{PIN_D / 2 * K:.1f}"/>')
    r.rtext(X(0.42), Yr(1.75), "front-apron pins")
    r.rtext(X(3 * LEG + 1.05), Yr(2.65), "side-apron pin")
    # pin heights
    r.dim_v(0, PINS_LONG[0], X(0) - 24, frac(PINS_LONG[0]))
    r.dim_v(0, PINS_LONG[1], X(0) - 50, frac(PINS_LONG[1]))
    for c in (X(0) - 24, X(0) - 50):
        r.add(f'<line class="ext" x1="{c:.1f}" y1="{Yr(0):.1f}" x2="{X(0):.1f}" y2="{Yr(0):.1f}"/>')
    for v, c in zip(PINS_LONG, (X(0) - 24, X(0) - 50)):
        r.add(f'<line class="ext" x1="{c:.1f}" y1="{Yr(v):.1f}" x2="{X(pf_u):.1f}" y2="{Yr(v):.1f}"/>')
    ce, cz = X(4 * LEG) + 24, X(4 * LEG) + 50
    r.dim_v(0, PIN_SHORT, ce, frac(PIN_SHORT), left=False)
    r.dim_v(0, AP_H, cz, f"{frac(AP_H)} apron", left=False)
    for c in (ce, cz):
        r.add(f'<line class="ext" x1="{c:.1f}" y1="{Yr(0):.1f}" x2="{X(4 * LEG):.1f}" y2="{Yr(0):.1f}"/>')
    r.add(f'<line class="ext" x1="{ce:.1f}" y1="{Yr(PIN_SHORT):.1f}" x2="{X(pe_u):.1f}" y2="{Yr(PIN_SHORT):.1f}"/>')
    r.add(f'<line class="ext" x1="{cz:.1f}" y1="{Yr(AP_H):.1f}" x2="{X(3 * LEG - NEAR):.1f}" y2="{Yr(AP_H):.1f}"/>')
    # pin offsets from the shoulder faces
    rowb = Yr(VIS) + 28
    r.dim_h_small(pf_u, LEG, rowb, frac(PIN_IN), pyo=Yr(PINS_LONG[1]), side="left")
    r.dim_h_small(3 * LEG, pe_u, rowb, frac(PIN_IN), pyo=Yr(PIN_SHORT), side="right")

    # key: the leg in plan, looking down, front at the bottom
    kx0, ky0 = 560, 404
    k = CDrawing(1, 1, kx0, ky0, s=K)
    k.text(kx0 - 150, ky0 - 26, "key: plan of the leg, front at the bottom", "n", "start")
    k.rect(0, 0, LEG, LEG, "leg")
    k.rect(LEG - TEN, LEG - NL, LEG, LEG - NEAR, "mort")          # inner-face mortise (front apron)
    k.rect(NEAR, 0, NL, TEN, "mort")                              # back-face mortise (side apron)
    k.line(LEG - PIN_IN, LEG, LEG - PIN_IN, LEG - (NL + BLIND), "pinl")   # front pin
    k.line(0, PIN_IN, NL + BLIND, PIN_IN, "pinl")                         # end pin
    k.text(k.x(LEG / 2), k.y(LEG) + 16, "front", "n")
    k.text(k.x(LEG / 2), k.y(0) - 6, "back", "n")
    k.text(k.x(0) - 6, k.y(LEG / 2) + 4, "end", "n", "end")
    k.text(k.x(LEG) + 6, k.y(LEG / 2) + 4, "inner", "n", "start")
    for (u, v, dx, dy, s) in ((0, LEG, -8, 14, "A"), (LEG, LEG, 8, 14, "B"), (LEG, 0, 8, -4, "C"), (0, 0, -8, -4, "D")):
        k.text(k.x(u) + dx, k.y(v) + dy, s, "ts")

    d.p += r.p + k.p
    notes = [f"Front-left leg shown. The back-right leg is the same part turned end for end; the front-right and back-left legs are mirror images.",
             f"Mortises {frac(TEN_T)} wide × {frac(TEN)} deep, {frac32(NEAR)} in from the outer face (tenon centred on the {frac(STOCK_T)} apron or rail — see the drawbore section).",
             "Mortise length = tenon width, which this plan leaves to you (e.g. a haunch at the top). Pins Ø" + frac(PIN_D) +
             f", {frac(PIN_IN)} from the shoulder face, drilled",
             f"from the outer faces; stagger the 1–2 rail pins the same way. Blue ○ = pin, A–D = leg corners."]
    for i, s in enumerate(notes):
        d.text(20, 540 + 16 * i, s, "n", "start")
    d.save(path, "Cherry hallway console, leg layout", extra=EXTRA)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "..", "public", "static", "woodworking")
    os.makedirs(out, exist_ok=True)
    front(os.path.join(out, "cherry-console-front.svg"))
    side(os.path.join(out, "cherry-console-side.svg"))
    plan(os.path.join(out, "cherry-console-plan.svg"))
    drawbore(os.path.join(out, "cherry-console-drawbore.svg"))
    legs(os.path.join(out, "cherry-console-legs.svg"))
    print("wrote 5 SVGs to", os.path.normpath(out))
