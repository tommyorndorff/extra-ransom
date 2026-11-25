#!/usr/bin/env python3
"""Generate true-scale SVG drawings for the Modern Craftsman 2-drawer console plan.

Usage: python3 tools/woodworking/modern_craftsman_drawings.py
Writes public/static/woodworking/modern-craftsman-{front,side,plan}.svg
All geometry is in inches; S is pixels per inch. Edit the constants, re-run.
"""
import os

S = 12                      # px per inch
W, D, H = 60, 16, 29        # overall (stated)
OVH_END, OVH_FB = 8, 1      # overhangs (stated)
TOP_T = 0.75                # est.
LEG = 1.75                  # est.
FRAME_W = W - 2 * OVH_END   # 44
FRAME_D = D - 2 * OVH_FB    # 14
APRON_T, APRON_H = 0.75, 4.5
RAIL_T, RAIL_H = 1.25, 2.5  # shelf side rails
RAIL_TOP_OFF_FLOOR = 11.0
SHELF_TOP = 10.5
SHELF_T, SHELF_W, SHELF_D = 0.75, 41.5, 9.75
DR_W, DR_H, REVEAL, DIV = 19.75, 3.5, 1 / 16, 0.75
LOW_RAIL_H = 1.0

STYLE = """
<style>
  .bg{fill:#fff}
  .wood{fill:#ecd2ac;stroke:#4a3320;stroke-width:1.3;stroke-linejoin:round}
  .leg{fill:#dcb988;stroke:#4a3320;stroke-width:1.3}
  .face{fill:#f3dfbf;stroke:#4a3320;stroke-width:1.3}
  .pull{fill:#5a3b26;stroke:#2b1a0f;stroke-width:1}
  .shelf{fill:#e6c79c;stroke:#4a3320;stroke-width:1.3}
  .hid{fill:none;stroke:#7a6a5a;stroke-width:1.1;stroke-dasharray:5 3}
  .spacer{fill:#cfc3b4;stroke:#6b5b4b;stroke-width:1}
  .floor{stroke:#333;stroke-width:1.6}
  .dim{stroke:#1f5fa8;stroke-width:1;fill:none}
  .ext{stroke:#8fb0d8;stroke-width:.8}
  .t{font:12px 'Helvetica Neue',Arial,sans-serif;fill:#1f3a5f}
  .n{font:11px 'Helvetica Neue',Arial,sans-serif;fill:#444}
  .h{font:600 15px 'Helvetica Neue',Arial,sans-serif;fill:#222}
</style>
<defs>
  <marker id="a" viewBox="0 0 8 8" refX="8" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,0 L8,4 L0,8 z" fill="#1f5fa8"/>
  </marker>
</defs>
"""


def frac(v):
    """Inches → a label such as 13⅜″, to the nearest 1/16″. Use it to build labels
    from the constants so the drawing can't drift from the numbers."""
    glyph = {1: "1/16", 2: "⅛", 3: "3/16", 4: "¼", 5: "5/16", 6: "⅜", 7: "7/16", 8: "½",
             9: "9/16", 10: "⅝", 11: "11/16", 12: "¾", 13: "13/16", 14: "⅞", 15: "15/16"}
    n = round(v * 16)
    whole, rem = divmod(n, 16)
    if rem == 0:
        return f"{whole}″"
    return (f"{whole}" if whole else "") + glyph[rem] + "″"


class Drawing:
    def __init__(self, w, h, ox, oy, depth_up=False, s=S):
        self.w, self.h, self.ox, self.oy, self.p = w, h, ox, oy, []
        self.s = s
        self.depth_up = depth_up

    def x(self, v): return self.ox + v * self.s
    def y(self, v): return self.oy + v * self.s
    def add(self, s): self.p.append(s)

    def rect(self, x1, y1, x2, y2, cls):
        self.add(f'<rect class="{cls}" x="{self.x(x1):.2f}" y="{self.y(y1):.2f}" '
                 f'width="{(x2-x1)*self.s:.2f}" height="{(y2-y1)*self.s:.2f}"/>')

    def text(self, px, py, s, cls="n", anchor="middle"):
        self.add(f'<text class="{cls}" x="{px:.1f}" y="{py:.1f}" text-anchor="{anchor}">{s}</text>')

    # horizontal dimension: x1..x2 (in), at pixel row py; ext lines down to object row pyo
    def dim_h(self, x1, x2, py, label, pyo=None, below=False):
        a, b = self.x(x1), self.x(x2)
        if pyo is not None:
            for xx in (a, b):
                self.add(f'<line class="ext" x1="{xx:.1f}" y1="{py:.1f}" x2="{xx:.1f}" y2="{pyo:.1f}"/>')
        self.add(f'<line class="dim" x1="{a:.1f}" y1="{py:.1f}" x2="{b:.1f}" y2="{py:.1f}" '
                 f'marker-start="url(#a)" marker-end="url(#a)"/>')
        self.text((a + b) / 2, py + (15 if below else -5), label, "t")

    # vertical dimension
    def dim_v(self, y1, y2, px, label, pxo=None, left=True):
        a, b = self.y(y1), self.y(y2)
        if pxo is not None:
            for yy in (a, b):
                self.add(f'<line class="ext" x1="{px:.1f}" y1="{yy:.1f}" x2="{pxo:.1f}" y2="{yy:.1f}"/>')
        self.add(f'<line class="dim" x1="{px:.1f}" y1="{a:.1f}" x2="{px:.1f}" y2="{b:.1f}" '
                 f'marker-start="url(#a)" marker-end="url(#a)"/>')
        mid = (a + b) / 2
        if left:
            self.add(f'<text class="t" transform="translate({px-6:.1f},{mid:.1f}) rotate(-90)" text-anchor="middle">{label}</text>')
        else:
            self.add(f'<text class="t" transform="translate({px+14:.1f},{mid:.1f}) rotate(-90)" text-anchor="middle">{label}</text>')

    # ---- optional extras (added later; the methods above are unchanged, so
    # ---- scripts that don't call these produce byte-identical output) ----

    def line(self, x1, y1, x2, y2, cls="hid"):
        """Line between two points given in inches."""
        self.add(f'<line class="{cls}" x1="{self.x(x1):.1f}" y1="{self.y(y1):.1f}" '
                 f'x2="{self.x(x2):.1f}" y2="{self.y(y2):.1f}"/>')

    def poly(self, pts, cls="wood"):
        """Closed polygon from (x, y) points in inches."""
        self.add(f'<polygon class="{cls}" points="' +
                 ' '.join(f'{self.x(a):.1f},{self.y(b):.1f}' for a, b in pts) + '"/>')

    def leader(self, px1, py1, px2, py2, label, anchor="start", cls="n"):
        """Callout: thin line from a feature (px1, py1) to a label at (px2, py2), in pixels."""
        self.add(f'<line class="ext" x1="{px1:.1f}" y1="{py1:.1f}" x2="{px2:.1f}" y2="{py2:.1f}"/>')
        dx = 3 if anchor == "start" else -3 if anchor == "end" else 0
        self.text(px2 + dx, py2 + 4, label, cls, anchor)

    def dim_v_text(self, y1, y2, px, label, pxo=None, side="right", cls="t"):
        """Vertical dimension with an upright (unrotated) label beside it.
        Use for spans too short to hold a rotated label."""
        a, b = self.y(y1), self.y(y2)
        if pxo is not None:
            for yy in (a, b):
                self.add(f'<line class="ext" x1="{px:.1f}" y1="{yy:.1f}" x2="{pxo:.1f}" y2="{yy:.1f}"/>')
        self.add(f'<line class="dim" x1="{px:.1f}" y1="{a:.1f}" x2="{px:.1f}" y2="{b:.1f}" '
                 f'marker-start="url(#a)" marker-end="url(#a)"/>')
        if side == "right":
            self.text(px + 5, (a + b) / 2 + 4, label, cls, "start")
        else:
            self.text(px - 5, (a + b) / 2 + 4, label, cls, "end")

    def dim_h_small(self, x1, x2, py, label, pyo=None, side="right", cls="t"):
        """Horizontal dimension for a gap too small for inside arrows: arrows sit
        outside the extension lines and point in; the label goes beside."""
        a, b = self.x(x1), self.x(x2)
        if pyo is not None:
            for xx in (a, b):
                self.add(f'<line class="ext" x1="{xx:.1f}" y1="{py:.1f}" x2="{xx:.1f}" y2="{pyo:.1f}"/>')
        self.add(f'<line class="dim" x1="{a-14:.1f}" y1="{py:.1f}" x2="{a:.1f}" y2="{py:.1f}" marker-end="url(#a)"/>')
        self.add(f'<line class="dim" x1="{b+14:.1f}" y1="{py:.1f}" x2="{b:.1f}" y2="{py:.1f}" marker-end="url(#a)"/>')
        if side == "right":
            self.text(b + 18, py + 4, label, cls, "start")
        else:
            self.text(a - 18, py + 4, label, cls, "end")

    def save(self, path, title, extra=""):
        """`extra` is optional CSS/defs markup appended after the shared STYLE."""
        body = '\n'.join(self.p)
        svg = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
               f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
               f'width="{self.w}" height="{self.h}" role="img" aria-label="{title}">\n'
               f'<title>{title}</title>{STYLE}{extra}<rect class="bg" width="{self.w}" height="{self.h}"/>\n'
               f'{body}\n</svg>\n')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(svg)


# ---------------------------------------------------------------------------
# Modern Craftsman console: plan-specific numbers and views. Everything above
# this line is the shared helper (imported by the other plans' scripts).
# ---------------------------------------------------------------------------
LEG_L, LEG_R = OVH_END, OVH_END + FRAME_W - LEG          # leg left faces: 8, 50¼
OPEN_L, OPEN_R = LEG_L + LEG, LEG_R                      # opening between front legs: 9¾ .. 50¼
CX = (OPEN_L + OPEN_R) / 2                               # 30, centre of the frame
FL, FL2 = OVH_FB, OVH_FB + LEG                           # front legs, depth 1 .. 2¾
BL, BL2 = D - OVH_FB - LEG, D - OVH_FB                   # back legs, depth 13¼ .. 15
LEG_LEN = H - TOP_T                                      # 28¼
LOW_RAIL_T = 0.75                                        # lower front rail thickness (est.)
DR_TOP = TOP_T + REVEAL                                  # drawer-front top, down from the top surface
LOW_RAIL_TOP = DR_TOP + DR_H + REVEAL                    # 4⅜
DR_OPEN = (OPEN_R - OPEN_L - DIV) / 2                    # 19⅞ per bay
SHELF_X = LEG_L + RAIL_T                                 # 9¼
SHELF_DEP = FL2 + (BL - FL2 - SHELF_D) / 2               # 3⅛ (⅜ setback each side)
CLEAT = 0.75
PULL_L, PULL_H = 8, 0.625                                # (est.)
SPACER_T, SPACER_W, SPACER_L = 1, 3, 9
RUNNER_T, RUNNER_W = 0.75, 3
RUNNER_L = (BL2 - APRON_T) - (FL + LOW_RAIL_T)           # 12½, rail back face to back apron
FRONT_T = 0.75
# drawer box — stated interior 18 W × 7½ D × 2 H
DB_IN_W, DB_IN_D, DB_IN_H = 18, 7.5, 2
DB_SIDE_T, DB_BACK_T, DB_BOT_T, DB_H = 0.5, 0.5, 0.25, 2.5
DB_W = DB_IN_W + 2 * DB_SIDE_T                           # 19 box o/a
DB_D = FRONT_T + DB_IN_D + DB_BACK_T                     # 8¾ incl. front
DB_LAP = 0.25                                            # half-blind lap left on the front (derived)
DB_SIDE_L = (FRONT_T - DB_LAP) + DB_IN_D + DB_BACK_T     # 8½ — matches the cut list
DB_TOP = DR_H - DB_H                                     # box top, down from the front's top edge (box flush at bottom)
GROOVE = 0.25
SLIDE_GAP = (DR_OPEN - DB_W) / 2                         # 7/16 per side
SHELF_RAIL_V = LEG_LEN - RAIL_TOP_OFF_FLOOR              # 17¼ below the leg top
MORT_W, MORT_INSET = 5 / 16, 0.25
assert abs(DB_SIDE_L - 8.5) < 1e-9 and abs(DR_OPEN - 19.875) < 1e-9 and abs(RUNNER_L - 12.5) < 1e-9

EXTRA = """
<style>
  .beech{fill:#f7ead2;stroke:#4a3320;stroke-width:1.3}
  .beyond{fill:#f8f3ea;stroke:#9a8a7a;stroke-width:1}
  .dt{fill:url(#hatch);stroke:#4a3320;stroke-width:1}
  .mort{fill:#5a3b26;stroke:none}
</style>
<defs>
  <pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="5" stroke="#4a3320" stroke-width="0.9"/>
  </pattern>
</defs>
"""


class DepthDrawing(Drawing):
    """Plan-type view: y is depth from the front edge, front at the bottom."""
    def __init__(self, w, h, ox, oy, dmax, s=S):
        super().__init__(w, h, ox, oy, s=s)
        self.dmax = dmax

    def y(self, v): return self.oy + (self.dmax - v) * self.s

    def rect(self, x1, y1, x2, y2, cls):
        ya, yb = sorted((self.y(y1), self.y(y2)))
        self.add(f'<rect class="{cls}" x="{self.x(x1):.2f}" y="{ya:.2f}" '
                 f'width="{(x2-x1)*self.s:.2f}" height="{yb-ya:.2f}"/>')

    def ext(self, px1, py1, px2, py2):
        self.add(f'<line class="ext" x1="{px1:.1f}" y1="{py1:.1f}" x2="{px2:.1f}" y2="{py2:.1f}"/>')

    def vtext(self, px, py, s, cls="n"):
        self.add(f'<text class="{cls}" transform="translate({px:.1f},{py:.1f}) rotate(-90)" text-anchor="middle">{s}</text>')


def dim_v_small(d, y1, y2, px, label, pxo=None):
    """Vertical twin of Drawing.dim_h_small: for spans under ~12 px the arrows sit
    outside the extension lines and point in; the label goes to the right."""
    a, b = d.y(y1), d.y(y2)
    if pxo is not None:
        for yy in (a, b):
            d.add(f'<line class="ext" x1="{px:.1f}" y1="{yy:.1f}" x2="{pxo:.1f}" y2="{yy:.1f}"/>')
    d.add(f'<line class="dim" x1="{px:.1f}" y1="{a-14:.1f}" x2="{px:.1f}" y2="{a:.1f}" marker-end="url(#a)"/>')
    d.add(f'<line class="dim" x1="{px:.1f}" y1="{b+14:.1f}" x2="{px:.1f}" y2="{b:.1f}" marker-end="url(#a)"/>')
    d.text(px + 6, (a + b) / 2 + 4, label, "t", "start")


def front(path):
    d = Drawing(960, 540, 95, 100)
    d.text(20, 24, f"Front elevation — 1 in = {S} px", "h", "start")
    sy = H - SHELF_TOP
    d.rect(SHELF_X, sy, SHELF_X + SHELF_W, sy + SHELF_T, "shelf")       # behind the legs
    d.rect(0, 0, W, TOP_T, "wood")
    for x in (LEG_L, LEG_R):
        d.rect(x, TOP_T, x + LEG, H, "leg")
    d.rect(OPEN_L, LOW_RAIL_TOP, OPEN_R, LOW_RAIL_TOP + LOW_RAIL_H, "wood")
    d.rect(CX - DIV / 2, TOP_T, CX + DIV / 2, LOW_RAIL_TOP, "wood")
    for a, b in ((OPEN_L + REVEAL, CX - DIV / 2 - REVEAL), (CX + DIV / 2 + REVEAL, OPEN_R - REVEAL)):
        d.rect(a, DR_TOP, b, DR_TOP + DR_H, "face")
        mid = (a + b) / 2
        d.rect(mid - PULL_L / 2, DR_TOP + DR_H / 2 - PULL_H / 2,
               mid + PULL_L / 2, DR_TOP + DR_H / 2 + PULL_H / 2, "pull")
        d.text(d.x(mid), d.y(DR_TOP + 0.8), f"drawer front {frac(DR_W)} × {frac(DR_H)}")
        d.text(d.x(mid), d.y(DR_TOP + 3.05), f"walnut pull ≈ {frac(PULL_L)}")
    d.add(f'<line class="floor" x1="{d.x(-3):.1f}" y1="{d.y(H):.1f}" x2="{d.x(W+3):.1f}" y2="{d.y(H):.1f}"/>')
    d.text(d.x(CX), d.y(15), "open below drawers", "n")
    d.text(d.x(CX), d.y(sy) - 6, "lower shelf (ends hidden behind the front legs)", "n")
    # overall widths (top)
    d.dim_h(0, W, 42, f"{frac(W)} overall", pyo=d.y(0))
    d.dim_h(0, OVH_END, 68, frac(OVH_END), pyo=d.y(0))
    d.dim_h(OVH_END, OVH_END + FRAME_W, 68, f"{frac(FRAME_W)} leg frame", pyo=d.y(TOP_T))
    d.dim_h(OVH_END + FRAME_W, W, 68, frac(OVH_END), pyo=d.y(0))
    # drawer openings (just under the lower rail)
    yo = d.y(LOW_RAIL_TOP + LOW_RAIL_H) + 26
    for a, b in ((OPEN_L, CX - DIV / 2), (CX + DIV / 2, OPEN_R)):
        d.dim_h(a, b, yo, f"{frac(DR_OPEN)} opening", pyo=d.y(LOW_RAIL_TOP))
    # heights
    d.dim_v(0, H, 52, f"{frac(H)} overall", pxo=d.x(0))
    dim_v_small(d, 0, TOP_T, d.x(W) + 16, f"{frac(TOP_T)} top (est.)", pxo=d.x(W))
    px = d.x(LEG_R + LEG) + 30
    d.dim_v(TOP_T, LOW_RAIL_TOP, px, frac(LOW_RAIL_TOP - TOP_T), pxo=d.x(OPEN_R), left=False)
    d.dim_v_text(LOW_RAIL_TOP, LOW_RAIL_TOP + LOW_RAIL_H, px, f"{frac(LOW_RAIL_H)} lower rail",
                 pxo=d.x(OPEN_R))
    d.dim_v(sy, H, d.x(LEG_R) - 30, f"≈ {frac(SHELF_TOP)} (est.)")
    # legs + opening (bottom)
    yb = d.y(H) + 28
    d.dim_h(LEG_L, LEG_L + LEG, yb, frac(LEG), pyo=d.y(H), below=True)
    d.dim_h(OPEN_L, OPEN_R, yb, f"{frac(OPEN_R - OPEN_L)} opening", pyo=d.y(H), below=True)
    d.dim_h(LEG_R, LEG_R + LEG, yb, frac(LEG), pyo=d.y(H), below=True)
    d.text(d.x(CX), yb + 40,
           f"{frac(REVEAL)} reveals all round · {frac(DIV)} center divider · "
           f"{frac(LOW_RAIL_T)} × {frac(LOW_RAIL_H)} lower rail · "
           f"{frac(LOW_RAIL_TOP - TOP_T)} = drawer opening height under the top", "n")
    d.save(path, "Modern Craftsman console, front elevation")


def side(path):
    d = Drawing(560, 540, 95, 100)
    d.text(20, 24, f"Side elevation — 1 in = {S} px", "h", "start")
    d.rect(0, 0, D, TOP_T, "wood")
    d.rect(FL, TOP_T, FL2, H, "leg")
    d.rect(BL, TOP_T, BL2, H, "leg")
    d.rect(FL2, TOP_T, BL, TOP_T + APRON_H, "face")                    # side apron
    ry = H - RAIL_TOP_OFF_FLOOR
    d.rect(FL2, ry, BL, ry + RAIL_H, "face")                            # shelf side rail
    # hidden: shelf and its cleat behind the rail, drawer box behind the apron
    sy = H - SHELF_TOP
    d.rect(SHELF_DEP, sy, SHELF_DEP + SHELF_D, sy + SHELF_T, "hid")
    d.rect(SHELF_DEP, sy + SHELF_T, SHELF_DEP + SHELF_D, sy + SHELF_T + CLEAT, "hid")
    bt = DR_TOP + DB_TOP
    d.rect(FL, bt, FL + DB_D, bt + DB_H, "hid")
    d.text(d.x((FL2 + FL + DB_D) / 2), d.y(bt + DB_H / 2) + 4, "drawer box", "n")
    d.text(d.x(D / 2), d.y(TOP_T + APRON_H) + 14, f"side apron {frac(APRON_T)} × {frac(APRON_H)}", "n")
    d.text(d.x(D / 2), d.y(ry + RAIL_H) + 14, f"shelf rail {frac(RAIL_T)} × {frac(RAIL_H)}", "n")
    d.text(d.x(D / 2), d.y(ry + RAIL_H) + 28, "shelf + cleat dashed behind it", "n")
    d.add(f'<line class="floor" x1="{d.x(-3):.1f}" y1="{d.y(H):.1f}" x2="{d.x(D+3):.1f}" y2="{d.y(H):.1f}"/>')
    d.text(d.x(FL2) + 4, d.y(H) - 8, "◀ front", "n", "start")
    # depths (top)
    d.dim_h(0, D, 42, f"{frac(D)} overall", pyo=d.y(0))
    d.dim_h_small(0, OVH_FB, 68, frac(OVH_FB), pyo=d.y(TOP_T), side="left")
    d.dim_h_small(D - OVH_FB, D, 68, frac(OVH_FB), pyo=d.y(TOP_T), side="right")
    # heights, left
    d.dim_v(0, H, 52, f"{frac(H)} overall", pxo=d.x(0))
    d.dim_v(TOP_T, H, 76, f"{frac(LEG_LEN)} leg", pxo=d.x(FL))
    # heights, right
    p1 = d.x(D) + 20
    dim_v_small(d, 0, TOP_T, p1, f"{frac(TOP_T)} top (est.)", pxo=d.x(D))
    d.dim_v(TOP_T, TOP_T + APRON_H, p1, frac(APRON_H), pxo=d.x(BL), left=False)
    d.dim_v(ry, ry + RAIL_H, p1, frac(RAIL_H), pxo=d.x(BL), left=False)
    d.dim_v(ry, H, p1 + 44, f"{frac(RAIL_TOP_OFF_FLOOR)} to rail top (est.)", pxo=d.x(BL), left=False)
    # legs (bottom), frame on the outer row
    yb = d.y(H) + 28
    d.dim_h(FL, FL2, yb, frac(LEG), pyo=d.y(H), below=True)
    d.dim_h(FL2, BL, yb, f"{frac(BL - FL2)} between legs", pyo=d.y(H), below=True)
    d.dim_h(BL, BL2, yb, frac(LEG), pyo=d.y(H), below=True)
    d.dim_h(FL, BL2, yb + 28, f"{frac(BL2 - FL)} leg frame", pyo=d.y(H), below=True)
    d.save(path, "Modern Craftsman console, side elevation")


def plan(path):
    d = DepthDrawing(960, 380, 95, 100, D)
    d.text(20, 24, f"Plan view, top removed — 1 in = {S} px", "h", "start")
    d.rect(0, 0, W, D, "hid")                                           # top outline
    for x in (LEG_L, LEG_R + LEG - RAIL_T):                             # shelf side rails
        d.rect(x, FL2, x + RAIL_T, BL, "face")
    d.rect(SHELF_X, SHELF_DEP, SHELF_X + SHELF_W, SHELF_DEP + SHELF_D, "shelf")
    d.text(d.x(18), d.y(11.5), f"lower shelf {frac(SHELF_W)} × {frac(SHELF_D)}", "n")
    for x in (LEG_L, LEG_R + LEG - APRON_T):                            # side aprons
        d.rect(x, FL2, x + APRON_T, BL, "wood")
    d.rect(LEG_L + APRON_T, FL2, LEG_L + APRON_T + SPACER_T, FL2 + SPACER_L, "spacer")
    d.rect(LEG_R + LEG - APRON_T - SPACER_T, FL2, LEG_R + LEG - APRON_T, FL2 + SPACER_L, "spacer")
    d.rect(OPEN_L, BL2 - APRON_T, OPEN_R, BL2, "wood")                  # back apron
    d.rect(CX - RUNNER_T / 2, FL + LOW_RAIL_T, CX + RUNNER_T / 2, FL + LOW_RAIL_T + RUNNER_L, "wood")
    for x in (LEG_L, LEG_R):
        d.rect(x, FL, x + LEG, FL2, "leg")
        d.rect(x, BL, x + LEG, BL2, "leg")
    for c in (CX - DIV / 2 - REVEAL - DR_W / 2, CX + DIV / 2 + REVEAL + DR_W / 2):
        d.rect(c - DR_W / 2, FL, c + DR_W / 2, FL + FRONT_T, "face")
        d.rect(c - DB_W / 2, FL + FRONT_T, c + DB_W / 2, FL + DB_D, "hid")
        d.text(d.x(c), d.y(FL + 4.9), f"drawer box {frac(DB_W)} × {frac(DB_D)} o/a", "n")
        d.text(d.x(c), d.y(FL + 3.9), "(dashed; hangs on side-mount slides)", "n")
    d.rect(CX - DIV / 2, FL, CX + DIV / 2, FL + FRONT_T, "wood")
    d.text(d.x(CX + 1), d.y(11.5), f"◀ center runner {frac(RUNNER_T)}", "n", "start")
    d.text(d.x(CX), d.y(0) + 16, "FRONT", "n")
    d.text(d.x(0), d.y(0) + 46,
           f"Dashed outline = top, {frac(W)} × {frac(D)} × {frac(TOP_T)}, floating on buttons.  Dark tan = legs.  "
           f"Grey = {frac(SPACER_T)} × {frac(SPACER_W)} × {frac(SPACER_L)} drawer-slide spacers on the side aprons.",
           "n", "start")
    d.text(d.x(0), d.y(0) + 62,
           f"Slide faces (spacer to runner) are {frac(DR_OPEN)} apart; the {frac(DB_W)} drawer box leaves "
           f"{frac(SLIDE_GAP)} per side — see the drawer-bay detail.", "n", "start")
    # widths (top)
    d.dim_h(0, W, 42, f"{frac(W)} overall", pyo=d.y(D))
    d.dim_h(0, OVH_END, 68, frac(OVH_END), pyo=d.y(D))
    d.dim_h(OVH_END, OVH_END + FRAME_W, 68, f"{frac(FRAME_W)} leg frame", pyo=d.y(BL2))
    d.dim_h(OVH_END + FRAME_W, W, 68, frac(OVH_END), pyo=d.y(D))
    # depths: frame inside, overall outside; between-legs on the left
    d.dim_v(FL, BL2, d.x(W) + 24, f"{frac(BL2 - FL)} leg frame", pxo=d.x(LEG_R + LEG), left=False)
    d.dim_v(0, D, d.x(W) + 54, f"{frac(D)} overall", pxo=d.x(W), left=False)
    d.dim_v(FL2, BL, d.x(LEG_L) - 22, f"{frac(BL - FL2)} between legs", pxo=d.x(LEG_L))
    d.save(path, "Modern Craftsman console, plan view")


def drawer(path):
    """Left drawer bay in plan section at drawer height (1 in = 20 px), and a
    side section through the middle of a drawer box (1 in = 24 px)."""
    s1 = 20
    d = DepthDrawing(960, 440, 60 - 7 * s1, 60, 15.5, s=s1)
    d.text(20, 24, f"Drawer bay — plan section at drawer height, 1 in = {s1} px", "h", "start")
    box_c = (OPEN_L + REVEAL + CX - DIV / 2 - REVEAL) / 2
    bl, br = box_c - DB_W / 2, box_c + DB_W / 2
    rf = CX - RUNNER_T / 2                                              # runner face
    # case parts (cut)
    d.rect(LEG_L, FL, LEG_L + LEG, FL2, "leg")
    d.rect(LEG_L, BL, LEG_L + LEG, BL2, "leg")
    d.rect(LEG_L, FL2, LEG_L + APRON_T, BL, "wood")
    d.rect(LEG_L + APRON_T, FL2, OPEN_L, FL2 + SPACER_L, "spacer")
    d.rect(OPEN_L, BL2 - APRON_T, 31.25, BL2, "wood")                   # back apron (continues)
    d.rect(rf, FL + LOW_RAIL_T, rf + RUNNER_T, FL + LOW_RAIL_T + RUNNER_L, "wood")
    d.rect(CX - DIV / 2, FL, CX + DIV / 2, FL + FRONT_T, "wood")        # divider
    # drawer: front, bottom seen below, sides, back, dovetailed corners hatched
    d.rect(OPEN_L + REVEAL, FL, CX - DIV / 2 - REVEAL, FL + FRONT_T, "face")
    d.rect(bl + DB_SIDE_T, FL + FRONT_T, br - DB_SIDE_T, FL + DB_D - DB_BACK_T, "beyond")
    for x in (bl, br - DB_SIDE_T):
        d.rect(x, FL + DB_LAP, x + DB_SIDE_T, FL + DB_D, "beech")
        d.rect(x, FL + DB_LAP, x + DB_SIDE_T, FL + FRONT_T, "dt")
        d.rect(x, FL + DB_D - DB_BACK_T, x + DB_SIDE_T, FL + DB_D, "dt")
    d.rect(bl + DB_SIDE_T, FL + DB_D - DB_BACK_T, br - DB_SIDE_T, FL + DB_D, "beech")
    # in-part labels (rotated, parts ≥ 15 px wide)
    d.vtext(d.x(LEG_L + APRON_T / 2) + 4, d.y((FL2 + BL) / 2), "side apron")
    d.vtext(d.x(LEG_L + APRON_T + SPACER_T / 2) + 4, d.y(FL2 + SPACER_L / 2),
            f"spacer {frac(SPACER_T)} × {frac(SPACER_W)} × {frac(SPACER_L)}")
    d.vtext(d.x(CX) + 4, d.y(FL + LOW_RAIL_T + RUNNER_L / 2),
            f"center runner {frac(RUNNER_T)} × {frac(RUNNER_W)}")
    d.text(d.x(box_c), d.y(FL + FRONT_T + 2.0), f"bottom {frac(DB_BOT_T)} (seen below)", "n")
    d.text(d.x(box_c), d.y(FL + FRONT_T + 1.2), f"sides + back {frac(DB_SIDE_T)} beech", "n")
    # inside the box
    d.dim_h(bl + DB_SIDE_T, br - DB_SIDE_T, d.y(FL + FRONT_T + 4.6), f"{frac(DB_IN_W)} inside (stated)")
    d.dim_v(FL + FRONT_T, FL + DB_D - DB_BACK_T, d.x(bl + DB_SIDE_T) + 34,
            f"{frac(DB_IN_D)} inside (stated)", left=False)
    # behind the box: box width, slide gaps, slide-face spacing
    ybk = d.y(FL + DB_D)
    yB = ybk - 20
    d.dim_h(bl, br, yB, f"{frac(DB_W)} box o/a", pyo=ybk)
    yC = yB - 26
    d.dim_h_small(OPEN_L, bl, yC, frac(SLIDE_GAP), side="right")
    d.dim_h_small(br, rf, yC, frac(SLIDE_GAP), side="left")
    d.ext(d.x(OPEN_L), yC, d.x(OPEN_L), d.y(FL2 + SPACER_L))
    d.ext(d.x(bl), yC, d.x(bl), ybk)
    d.ext(d.x(br), yC, d.x(br), ybk)
    yD = yC - 26
    d.dim_h(OPEN_L, rf, yD, f"{frac(DR_OPEN)} between slide faces", below=True)
    d.ext(d.x(OPEN_L), yD, d.x(OPEN_L), yC)
    # depths: drawer o/a and runner on the right, spacer on the left
    p1 = d.x(rf + RUNNER_T) + 22
    d.dim_v(FL, FL + DB_D, p1, f"{frac(DB_D)} drawer o/a", pxo=d.x(br), left=False)
    d.dim_v(FL + LOW_RAIL_T, FL + LOW_RAIL_T + RUNNER_L, p1 + 30, f"{frac(RUNNER_L)} runner",
            pxo=d.x(rf + RUNNER_T), left=False)
    d.dim_v(FL2, FL2 + SPACER_L, d.x(LEG_L) - 20, f"{frac(SPACER_L)} spacer", pxo=d.x(LEG_L + APRON_T))
    d.text(d.x(box_c), d.y(0.5) + 4, "FRONT", "n")
    d.text(20, 392, "Cut parts solid; drawer bottom (light) seen below; hatched = dovetailed corners. "
                    "Right bay mirrors this one about the runner.", "n", "start")
    d.text(20, 408, f"The stated {frac(DB_IN_W)} interior + two {frac(DB_SIDE_T)} sides = {frac(DB_W)} box; the bay is "
                    f"{frac(DR_OPEN)} between slide faces, so {frac(SLIDE_GAP)} per side —", "n", "start")
    d.text(20, 424, f"{frac(0.5 - SLIDE_GAP)} short of ½″ side-mount slides. See Open questions on the plan page.",
           "n", "start")

    # side section through the middle of the box
    s2 = 24
    e = Drawing(0, 0, 650, 150, s=s2)
    e.text(640, 92, f"Drawer box — side section, 1 in = {s2} px", "h", "start")
    e.rect(FRONT_T, DB_TOP, FRONT_T + DB_IN_D, DR_H, "beyond")           # side, seen beyond
    e.rect(0, 0, FRONT_T, DR_H, "face")                                 # front (cut)
    e.rect(FRONT_T + DB_IN_D, DB_TOP, DB_D, DR_H, "beech")               # back (cut)
    bot = DR_H - (DB_H - DB_IN_H)                                       # bottom's upper face
    e.rect(FRONT_T - GROOVE, bot, FRONT_T + DB_IN_D + GROOVE, bot + DB_BOT_T, "beech")
    e.line(DB_LAP, DB_TOP, DB_LAP, DR_H, "hid")                         # side's end inside the front
    e.line(DB_LAP, DB_TOP, FRONT_T, DB_TOP, "hid")
    e.dim_h_small(0, FRONT_T, e.y(0) - 14, frac(FRONT_T), pyo=e.y(0), side="right")
    e.dim_h(FRONT_T, FRONT_T + DB_IN_D, e.y(DB_TOP + 1.05), f"{frac(DB_IN_D)} inside")
    e.dim_v(0, DR_H, e.x(0) - 22, f"{frac(DR_H)} front", pxo=e.x(0))
    e.dim_v(DB_TOP, bot, e.x(DB_D) + 20, frac(DB_IN_H), pxo=e.x(FRONT_T + DB_IN_D + GROOVE), left=False)
    e.dim_v(DB_TOP, DR_H, e.x(DB_D) + 46, f"{frac(DB_H)} side", pxo=e.x(DB_D), left=False)
    yb = e.y(DR_H) + 24
    e.dim_h(DB_LAP, DB_D, yb, f"{frac(DB_SIDE_L)} side", pyo=e.y(DR_H), below=True)
    e.dim_h(0, DB_D, yb + 28, f"{frac(DB_D)} overall", pyo=e.y(DR_H), below=True)
    for i, line in enumerate((
            "Front cherry (cut); side seen beyond; back and bottom beech.",
            f"Bottom {frac(DB_BOT_T)} in {frac(GROOVE)} × {frac(GROOVE)} grooves, its top face",
            f"{frac(DB_H - DB_IN_H)} up (derived: {frac(DB_H)} − {frac(DB_IN_H)} inside).",
            f"Half-blind dovetails at the front leave a {frac(DB_LAP)} lap (derived",
            f"from the {frac(DB_SIDE_L)} side); through dovetails at the back.",
            "Box bottom flush with the front's lower edge (est.).")):
        e.text(640, 330 + 15 * i, line, "n", "start")
    d.p.extend(e.p)
    d.save(path, "Modern Craftsman console, drawer bay and drawer box", extra=EXTRA)


def legs(path):
    """Each leg face that takes a rail, at true length, measured down from the leg top."""
    s = 16
    d = Drawing(960, 650, 0, 0, s=s)
    d.text(20, 24, f"Leg layout — rail positions on each leg face, 1 in = {s} px", "h", "start")
    apron = ("side apron", APRON_T, 0, APRON_H)
    shelf = ("shelf rail", RAIL_T, SHELF_RAIL_V, SHELF_RAIL_V + RAIL_H)
    faces = (
        ("Front legs", "back face", "inside", "outside", (apron, shelf)),
        ("Front legs", "inside face", "back", "front",
         (("lower front rail", LOW_RAIL_T, LOW_RAIL_TOP - TOP_T, LOW_RAIL_TOP - TOP_T + LOW_RAIL_H),)),
        ("Back legs", "front face", "inside", "outside", (apron, shelf)),
        ("Back legs", "inside face", "front", "back", (("back apron", APRON_T, 0, APRON_H),)),
    )
    oy = 112
    for i, (t1, t2, other, flush, zones) in enumerate(faces):
        x0 = 165 + i * 210
        g = Drawing(0, 0, x0, oy, s=s)
        cx = g.x(LEG / 2)
        g.text(cx, oy - 58, t1, "h")
        g.text(cx, oy - 42, t2, "n")
        g.text(g.x(0) - 2, oy - 8, other, "n", "end")
        g.text(g.x(LEG) + 2, oy - 8, flush, "n", "start")
        g.rect(0, 0, LEG, LEG_LEN, "leg")
        cuts = {0.0, LEG_LEN}
        for name, t, v1, v2 in zones:
            g.rect(LEG - t, v1, LEG, v2, "face")
            g.rect(LEG - t / 2 - MORT_W / 2, v1 + MORT_INSET, LEG - t / 2 + MORT_W / 2, v2 - MORT_INSET, "mort")
            ym = g.y((v1 + v2) / 2)
            g.text(g.x(0) - 6, ym - 3, name, "n", "end")
            g.text(g.x(0) - 6, ym + 11, f"{frac(t)} × {frac(v2 - v1)}", "n", "end")
            cuts |= {v1, v2}
        cuts = sorted(cuts)
        px = g.x(LEG) + 22
        for a, b in zip(cuts, cuts[1:]):
            if (b - a) * s < 25:
                g.dim_v_text(a, b, px, frac(b - a), pxo=g.x(LEG))
            else:
                g.dim_v(a, b, px, frac(b - a), pxo=g.x(LEG), left=False)
        if i == 0:
            g.dim_v(0, LEG_LEN, g.x(0) - 100, f"{frac(LEG_LEN)} leg (all four)", pxo=g.x(0))
        d.p.extend(g.p)
    yn = oy + LEG_LEN * s + 30
    for k, line in enumerate((
            "Measured down from the leg top (= underside of the table top). Shaded = where the rail meets the leg, "
            "flush to the edge named; dark = mortise.",
            f"Mortises {frac(MORT_W)}–⅜″ wide, 1″ deep, centred on the rail's thickness; ends {frac(MORT_INSET)} in "
            "from the rail's edges (suggested). Miter tenon tips where two meet.",
            "Right-hand legs are mirror images. For a Domino build, stagger the mortises instead (see Domino option).")):
        d.text(20, yn + 16 * k, line, "n", "start")
    d.save(path, "Modern Craftsman console, leg layout", extra=EXTRA)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "..", "public", "static", "woodworking")
    os.makedirs(out, exist_ok=True)
    front(os.path.join(out, "modern-craftsman-front.svg"))
    side(os.path.join(out, "modern-craftsman-side.svg"))
    plan(os.path.join(out, "modern-craftsman-plan.svg"))
    drawer(os.path.join(out, "modern-craftsman-drawer.svg"))
    legs(os.path.join(out, "modern-craftsman-legs.svg"))
    print("wrote 5 SVGs to", os.path.normpath(out))
