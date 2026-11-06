#!/usr/bin/env python3
"""Generate true-scale SVG drawings for the Modern Craftsman 2-drawer console plan.

Usage: python3 tools/woodworking/modern_craftsman_drawings.py
Writes static/static/woodworking/modern-craftsman-{front,side,plan}.svg
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

    def save(self, path, title):
        body = '\n'.join(self.p)
        svg = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
               f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
               f'width="{self.w}" height="{self.h}" role="img" aria-label="{title}">\n'
               f'<title>{title}</title>{STYLE}<rect class="bg" width="{self.w}" height="{self.h}"/>\n'
               f'{body}\n</svg>\n')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(svg)


def front(path):
    d = Drawing(920, 540, 95, 100)
    leg_l, leg_r = OVH_END, OVH_END + FRAME_W - LEG          # 8, 50.25
    d.text(20, 24, "Front elevation — 1 in = 12 px", "h", "start")
    # shelf (behind legs)
    d.rect(9.25, H - SHELF_TOP, 9.25 + SHELF_W, H - SHELF_TOP + SHELF_T, "shelf")
    # top, legs
    d.rect(0, 0, W, TOP_T, "wood")
    d.rect(leg_l, TOP_T, leg_l + LEG, H, "leg")
    d.rect(leg_r, TOP_T, leg_r + LEG, H, "leg")
    # lower front rail
    open_l, open_r = leg_l + LEG, leg_r
    r_top = TOP_T + REVEAL + DR_H + REVEAL
    d.rect(open_l, r_top, open_r, r_top + LOW_RAIL_H, "wood")
    # center divider
    cx = (open_l + open_r) / 2
    d.rect(cx - DIV / 2, TOP_T, cx + DIV / 2, r_top, "wood")
    # drawers
    dt = TOP_T + REVEAL
    x1 = open_l + REVEAL
    x2 = cx - DIV / 2 - REVEAL
    x3 = cx + DIV / 2 + REVEAL
    x4 = open_r - REVEAL
    for a, b in ((x1, x2), (x3, x4)):
        d.rect(a, dt, b, dt + DR_H, "face")
        mid = (a + b) / 2
        d.rect(mid - 4, dt + DR_H / 2 - 0.3, mid + 4, dt + DR_H / 2 + 0.3, "pull")
        d.text(d.x(mid), d.y(dt + 0.85), "19¾″ × 3½″", "n")
        d.text(d.x(mid), d.y(dt + 2.95), "walnut pull ≈ 8″", "n")
    # floor
    d.add(f'<line class="floor" x1="{d.x(-3):.1f}" y1="{d.y(H):.1f}" x2="{d.x(W+3):.1f}" y2="{d.y(H):.1f}"/>')
    d.text(d.x(30), d.y(15), "open below drawers", "n")
    d.text(d.x(30), d.y(18.5) - 6, "lower shelf (behind front legs)", "n")
    # dims top
    d.dim_h(0, W, 42, "60″ overall", pyo=d.y(0))
    d.dim_h(0, OVH_END, 68, "8″", pyo=d.y(0))
    d.dim_h(OVH_END, OVH_END + FRAME_W, 68, "44″ leg frame", pyo=d.y(TOP_T))
    d.dim_h(OVH_END + FRAME_W, W, 68, "8″", pyo=d.y(0))
    # left height
    d.dim_v(0, H, 52, "29″ overall", pxo=d.x(0))
    d.dim_v(0, TOP_T, d.x(W) + 22, "¾″ top (est.)", pxo=d.x(W), left=False)
    # shelf height right
    d.dim_v(H - SHELF_TOP, H, d.x(W) + 22 + 40, "≈ 10½″ to shelf top (est.)", pxo=d.x(W) + 4, left=False)
    # bottom
    yb = d.y(H) + 28
    d.dim_h(leg_l, leg_l + LEG, yb, "1¾″", pyo=d.y(H), below=True)
    d.dim_h(open_l, open_r, yb, "40½″ opening", pyo=d.y(H), below=True)
    d.dim_h(leg_r, leg_r + LEG, yb, "1¾″", pyo=d.y(H), below=True)
    d.text(d.x(30), yb + 40, "1/16″ reveals · ¾″ center divider · 1″ lower rail", "n")
    d.save(path, "Modern Craftsman console, front elevation")


def side(path):
    d = Drawing(560, 540, 95, 100)
    fl = OVH_FB                      # front leg depth start = 1
    fl2 = fl + LEG                   # 2.75
    bl = D - OVH_FB - LEG            # 13.25
    bl2 = D - OVH_FB                 # 15
    d.text(20, 24, "Side elevation — 1 in = 12 px", "h", "start")
    d.rect(0, 0, D, TOP_T, "wood")
    d.rect(fl, TOP_T, fl2, H, "leg")
    d.rect(bl, TOP_T, bl2, H, "leg")
    d.rect(fl2, TOP_T, bl, TOP_T + APRON_H, "face")       # side apron
    ry = H - RAIL_TOP_OFF_FLOOR
    d.rect(fl2, ry, bl, ry + RAIL_H, "face")              # shelf side rail
    # hidden drawer box behind apron
    bt = TOP_T + REVEAL + DR_H - 2.5
    d.add(f'<rect class="hid" x="{d.x(fl):.1f}" y="{d.y(bt):.1f}" width="{(0.75+7.5+0.5)*S:.1f}" height="{2.5*S:.1f}"/>')
    d.text(d.x(5.4), d.y(bt + 1.4), "drawer box (hidden)", "n")
    d.text(d.x(8), d.y(TOP_T + APRON_H) + 14, "side apron ¾″ × 4½″", "n")
    d.text(d.x(8), d.y(ry + RAIL_H / 2) + 4, "shelf rail 1¼″ × 2½″", "n")
    d.add(f'<line class="floor" x1="{d.x(-3):.1f}" y1="{d.y(H):.1f}" x2="{d.x(D+3):.1f}" y2="{d.y(H):.1f}"/>')
    d.text(d.x(0.5), d.y(H) - 8, "front", "n", "start")
    d.dim_h(0, D, 42, "16″ overall", pyo=d.y(0))
    d.dim_h(0, OVH_FB, 68, "1″", pyo=d.y(0))
    d.dim_h(OVH_FB, D - OVH_FB, 68, "14″ leg frame", pyo=d.y(TOP_T))
    d.dim_h(D - OVH_FB, D, 68, "1″", pyo=d.y(0))
    d.dim_v(0, H, 52, "29″ overall", pxo=d.x(0))
    d.dim_v(H - RAIL_TOP_OFF_FLOOR, H, d.x(D) + 30, "rail top ≈ 11″ off floor (est.)", pxo=d.x(bl2), left=False)
    yb = d.y(H) + 28
    d.dim_h(fl, fl2, yb, "1¾″", pyo=d.y(H), below=True)
    d.dim_h(fl2, bl, yb, "10½″ between legs", pyo=d.y(H), below=True)
    d.dim_h(bl, bl2, yb, "1¾″", pyo=d.y(H), below=True)
    d.save(path, "Modern Craftsman console, side elevation")


def plan(path):
    oy = 100
    d = Drawing(920, 372, 95, oy)
    Y = lambda dep: d.oy + (D - dep) * S          # front (depth 0) at bottom
    def prect(x1, dep1, x2, dep2, cls):
        d.add(f'<rect class="{cls}" x="{d.x(x1):.2f}" y="{Y(dep2):.2f}" '
              f'width="{(x2-x1)*S:.2f}" height="{(dep2-dep1)*S:.2f}"/>')
    d.text(20, 24, "Plan view, top removed — 1 in = 12 px", "h", "start")
    leg_l, leg_r = OVH_END, OVH_END + FRAME_W - LEG
    fl, fl2 = OVH_FB, OVH_FB + LEG
    bl, bl2 = D - OVH_FB - LEG, D - OVH_FB
    # top outline
    d.add(f'<rect class="hid" x="{d.x(0):.1f}" y="{Y(D):.1f}" width="{W*S}" height="{D*S}"/>')
    # shelf side rails, shelf
    for x in (leg_l, W - OVH_END - RAIL_T):
        prect(x, fl2, x + RAIL_T, bl, "face")
    prect(9.25, 3.125, 9.25 + SHELF_W, 3.125 + SHELF_D, "shelf")
    d.text(d.x(18), Y(11.5), "lower shelf 41½″ × 9¾″", "n")
    # side aprons + slide spacers
    for x in (leg_l, W - OVH_END - APRON_T):
        prect(x, fl2, x + APRON_T, bl, "wood")
    prect(leg_l + APRON_T, fl2, leg_l + LEG, fl2 + 9, "spacer")
    prect(leg_r, fl2, leg_r + LEG - APRON_T, fl2 + 9, "spacer")
    # back apron
    prect(leg_l + LEG, bl2 - APRON_T, leg_r, bl2, "wood")
    # center runner
    cx = (leg_l + LEG + leg_r) / 2
    prect(cx - 0.375, fl + 0.75, cx + 0.375, bl2 - APRON_T, "wood")
    # legs
    for x in (leg_l, leg_r):
        prect(x, fl, x + LEG, fl2, "leg")
        prect(x, bl, x + LEG, bl2, "leg")
    # drawers: box 18 7/8 wide centred on each front
    for c in (cx - DIV / 2 - REVEAL - DR_W / 2, cx + DIV / 2 + REVEAL + DR_W / 2):
        prect(c - DR_W / 2, fl, c + DR_W / 2, fl + 0.75, "face")
        bw = 18.875
        d.add(f'<rect class="hid" x="{d.x(c-bw/2):.1f}" y="{Y(fl+0.75+8.0):.1f}" '
              f'width="{bw*S:.1f}" height="{8.0*S:.1f}"/>')
        d.text(d.x(c), Y(fl + 4.9), "drawer box ≈ 18⅞″ × 8¾″", "n")
        d.text(d.x(c), Y(fl + 3.9), "(dashed; sits on slides)", "n")
    prect(cx - DIV / 2, fl, cx + DIV / 2, fl + 0.75, "wood")
    d.text(d.x(cx + 1), Y(11.5), "◀ center runner ¾″", "n", "start")
    # labels
    d.text(d.x(30), Y(0) + 16, "FRONT", "n")
    d.text(d.x(0), Y(0) + 46, "Dashed outline = top, 60″ × 16″ × ¾″, floating on buttons.  Dark tan = legs.  Grey = 1″ × 9″ drawer-slide spacers on the side aprons.", "n", "start")
    d.text(d.x(0), Y(0) + 62, "Drawer boxes (dashed) hang on side-mount slides: 1/2″ clearance each side, 29⅝″–30⅜″ center runner between them.", "n", "start")
    # dims
    d.dim_h(0, W, 42, "60″ overall", pyo=Y(D))
    d.dim_h(0, OVH_END, 68, "8″", pyo=Y(D))
    d.dim_h(OVH_END, OVH_END + FRAME_W, 68, "44″ leg frame", pyo=Y(bl2))
    d.dim_h(OVH_END + FRAME_W, W, 68, "8″", pyo=Y(D))
    px = d.x(W) + 24
    d.dim_v(0, 0, px, "", pxo=None)  # placeholder (no-op marker line)
    d.p.pop(); d.p.pop()
    # vertical dims use depth→y mapping, so draw manually
    def dim_depth(dep1, dep2, px, label):
        a, b = Y(dep1), Y(dep2)
        d.add(f'<line class="dim" x1="{px}" y1="{a:.1f}" x2="{px}" y2="{b:.1f}" marker-start="url(#a)" marker-end="url(#a)"/>')
        d.add(f'<text class="t" transform="translate({px+14},{(a+b)/2:.1f}) rotate(-90)" text-anchor="middle">{label}</text>')
    dim_depth(0, D, d.x(W) + 24, "16″ overall")
    dim_depth(fl, bl2, d.x(W) + 54, "14″ leg frame")
    dim_depth(fl2, bl, d.x(0) - 24, "10½″ between legs")
    d.save(path, "Modern Craftsman console, plan view")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "..", "static", "static", "woodworking")
    os.makedirs(out, exist_ok=True)
    front(os.path.join(out, "modern-craftsman-front.svg"))
    side(os.path.join(out, "modern-craftsman-side.svg"))
    plan(os.path.join(out, "modern-craftsman-plan.svg"))
    print("wrote 3 SVGs to", os.path.normpath(out))
