#!/usr/bin/env python3
"""True-scale SVGs for the miter-slot tenoning jig plan.

Usage: python3 tools/woodworking/tenoning_jig_drawings.py
Writes static/static/woodworking/tenoning-jig-{end,plan,cuts}.svg
Geometry in inches. X is across the saw (blade to the right), Y is the feed direction
in the plan view. A = fence face to the blade's near (left) plane.
Printed-part sizes come from static/static/woodworking-3d/generate_woodworking_stls.py.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from modern_craftsman_drawings import Drawing, frac

MM = 1 / 25.4
A = 1.25
BASE_T, FENCE_T = 0.75, 0.75
BASE_W, BASE_L = 7.0, 16.0
FENCE_H = 10.0                       # fence stands on the base
KERF = 0.125
BLADE_UP = 1.5                       # blade height above the table (= tenon length)
T_STOCK, T_TENON = 0.75, 0.375       # example stock t and tenon T
CHEEK = (T_STOCK + T_TENON) / 2      # shim face to blade near plane, 9/16
WASTE = (T_STOCK - T_TENON) / 2      # per side, 3/16
SHIM = A - CHEEK                     # 11/16
SHIM_SET = (1 / 2, 1 / 2, 1 / 4, 1 / 8, 1 / 16)
SHIM_PLATE_H, SHIM_PLATE_L = 70 * MM, 110 * MM     # printed plate, 70 x 110 mm
SLOT_W, SLOT_D = 0.75, 0.375                       # miter slot
RUN_W, RUN_H, RUN_L = 18.6 * MM, 8.8 * MM, 240 * MM
RUN_POCKET0, RUN_PITCH, RUN_POCKETS = 20 * MM, 40 * MM, 6
SLOT_X = -5.1                        # miter-slot centre (saw-dependent; drawn typical)
BSLOT_W, BSLOT_L = 7 / 32, 1.375     # base cross slots
BSLOT_PITCH = 2 * RUN_PITCH          # 80 mm: every other nut pocket
BR_L, BR_W, BR_T = 60 * MM, 40 * MM, 6 * MM        # fence bracket
BR_Y = (1.5, BASE_L - 1.5)           # bracket centres, near each end
HD_FX, HD_FY, HD_FT = 40 * MM, 60 * MM, 8 * MM     # handle flange
HD_POST, HD_POST_H, HD_KNOB = 28 * MM, 70 * MM, 36 * MM
HD_X, HD_Y = -3.4, BASE_L / 2 + BSLOT_PITCH / 2    # handle (position to suit)
STOCK_H, STOCK_W = 9.5, 3.5          # stock as drawn (length standing up, width)
UP_STACK_Z = 6.25                    # bottom of the upper shim stack
CLAMP_Z = 7.6                        # clamp pad height

EXTRA = """<style>
  .tjb{fill:#f1ede7;stroke:#8a8a8a;stroke-width:1}
  .tjk{fill:#444;stroke:#222;stroke-width:1}
  .tjs{fill:#fff;stroke:#4a3320;stroke-width:1}
  .tjw{fill:url(#tjh);stroke:#4a3320;stroke-width:.8}
  .tjc{fill:none;stroke:#666;stroke-width:3;stroke-linejoin:round}
  .tjt{fill:#d9d9d9;stroke:#555;stroke-width:1.2}
</style>
<defs>
  <pattern id="tjh" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="6" stroke="#9c7a52" stroke-width="1.1"/>
  </pattern>
</defs>
"""


def shim_combo(s):
    """Plates from SHIM_SET that sum to s, largest first."""
    out, left = [], round(s * 16)
    for p in SHIM_SET:
        if round(p * 16) <= left:
            out.append(p)
            left -= round(p * 16)
    assert left == 0, f"no shim stack for {s}"
    return out


def plate_frac(p):
    return frac(p).rstrip("″")


def end(path):
    K = 34
    d = Drawing(800, 690, 380, 120, s=K)
    zt = 11.0                                   # table surface (inches, y down)
    Z = lambda h: d.y(zt - h)                   # height above the table -> px
    TT = 1.3
    d.text(20, 24, "End view looking along the feed — 1 in = 34 px", "h", "start")
    # table, miter slot, runner (rests on the slot bottom, just below the surface)
    d.rect(-7.6, zt, 3.8, zt + TT, "tjt")
    d.rect(SLOT_X - SLOT_W / 2, zt, SLOT_X + SLOT_W / 2, zt + SLOT_D, "tjs")
    d.rect(SLOT_X - RUN_W / 2, zt + SLOT_D - RUN_H, SLOT_X + RUN_W / 2, zt + SLOT_D, "spacer")
    d.text(d.x(3.8) - 6, Z(0) + TT * K - 6, "table", "n", "end")
    d.text(d.x(SLOT_X + 0.65), Z(0) + 24, f"runner in {frac(SLOT_W)} × {frac(SLOT_D)} slot", "n", "start")
    # base, fence (on the base, face flush with the base edge)
    d.rect(-BASE_W, zt - BASE_T, 0, zt, "face")
    d.rect(-FENCE_T, zt - BASE_T - FENCE_H, 0, zt - BASE_T, "wood")
    d.text(d.x(-5.4), Z(BASE_T / 2) + 4, f"base {frac(BASE_T)} ply", "n")
    d.text(d.x(-FENCE_T) - 8, Z(6.6), f"fence {frac(FENCE_T)} ply", "n", "end")
    # handle and bracket, light fill (seen beyond the section)
    zb = BASE_T
    d.rect(HD_X - HD_POST / 2, zt - zb - HD_POST_H, HD_X + HD_POST / 2, zt - zb - HD_FT, "tjb")
    d.add(f'<circle class="tjb" cx="{d.x(HD_X):.1f}" cy="{Z(zb + HD_POST_H):.1f}" r="{HD_KNOB / 2 * K:.1f}"/>')
    d.rect(HD_X - HD_FX / 2, zt - zb - HD_FT, HD_X + HD_FX / 2, zt - zb, "tjb")
    cx = -FENCE_T
    d.poly([(cx, zt - zb), (cx - BR_L, zt - zb), (cx - BR_L, zt - zb - BR_T),
            (cx - BR_T, zt - zb - BR_L), (cx, zt - zb - BR_L)], "tjb")
    d.leader(d.x(HD_X - HD_KNOB / 2), Z(zb + HD_POST_H), d.x(-6.4), Z(zb + HD_POST_H + 0.9), "handle", "end")
    d.leader(d.x(cx - 1.0), Z(zb + 0.9), d.x(-6.4), Z(zb + 1.9), "bracket", "end")
    # shims: two stacks of plates, at the foot and at the clamp
    combo = shim_combo(SHIM)
    for z0 in (0.0, UP_STACK_Z):
        xc = 0.0
        for p in combo:
            d.rect(xc, zt - z0 - SHIM_PLATE_H, xc + p, zt - z0, "spacer")
            xc += p
    # stock and blade
    d.rect(SHIM, zt - STOCK_H, SHIM + T_STOCK, zt, "shelf")
    d.rect(A, zt - BLADE_UP, A + KERF, zt, "tjk")
    xr_lab = d.x(SHIM + T_STOCK) + 22
    d.text(xr_lab, Z(3.4), "stock, stands on the table", "n", "start")
    d.text(d.x(A + KERF + 0.3), Z(0.75) + 4, f"blade ({frac(KERF)} kerf)", "n", "start")
    sh = " + ".join(plate_frac(p) for p in combo)
    d.leader(d.x(SHIM / 2), Z(SHIM_PLATE_H / 2), xr_lab, Z(5.0), "", "start")
    d.leader(d.x(SHIM / 2), Z(UP_STACK_Z + SHIM_PLATE_H / 2), xr_lab, Z(5.0), "", "start")
    d.text(xr_lab + 3, Z(5.0) + 4, f"shim stacks {sh} = {frac(SHIM)}", "n", "start")
    d.text(xr_lab + 3, Z(5.0) + 18, "(printed plates, at the foot and at the clamp)", "n", "start")
    # C-clamp: pads on the fence back and the stock face, frame over the tops
    top = BASE_T + FENCE_H + 0.35
    xf, xs = d.x(-FENCE_T), d.x(SHIM + T_STOCK)
    xl, xr = d.x(-FENCE_T - 0.3), d.x(SHIM + T_STOCK + 0.3)
    d.add(f'<path class="tjc" d="M{xf:.1f},{Z(CLAMP_Z):.1f} L{xl:.1f},{Z(CLAMP_Z):.1f} L{xl:.1f},{Z(top):.1f} '
          f'L{xr:.1f},{Z(top):.1f} L{xr:.1f},{Z(CLAMP_Z):.1f} L{xs:.1f},{Z(CLAMP_Z):.1f}"/>')
    for x0 in (-FENCE_T - 0.12, SHIM + T_STOCK):
        d.rect(x0, zt - CLAMP_Z - 0.25, x0 + 0.12, zt - CLAMP_Z + 0.25, "pull")
    d.text((xl + xr) / 2, Z(top) - 8, "C-clamp: fence back to stock face, above the blade", "n")
    # A, from the fence face (top) to the blade's near plane
    d.dim_h(0, A, 62, f"A = {frac(A)} fence face to blade's near plane")
    d.add(f'<line class="ext" x1="{d.x(0):.1f}" y1="62" x2="{d.x(0):.1f}" y2="{Z(BASE_T + FENCE_H):.1f}"/>')
    d.add(f'<line class="ext" x1="{d.x(A):.1f}" y1="62" x2="{d.x(A):.1f}" y2="{Z(BLADE_UP):.1f}"/>')
    # left: fence height and base thickness
    px = 100
    d.dim_v(zt - BASE_T - FENCE_H, zt - BASE_T, px, f"fence {frac(FENCE_H)}")
    d.add(f'<line class="ext" x1="{px}" y1="{Z(BASE_T + FENCE_H):.1f}" x2="{d.x(-FENCE_T):.1f}" y2="{Z(BASE_T + FENCE_H):.1f}"/>')
    d.add(f'<line class="ext" x1="{px}" y1="{Z(BASE_T):.1f}" x2="{d.x(-BASE_W):.1f}" y2="{Z(BASE_T):.1f}"/>')
    d.dim_v_text(zt - BASE_T, zt, px, f"base {frac(BASE_T)}", side="left")
    d.add(f'<line class="ext" x1="{px}" y1="{Z(0):.1f}" x2="{d.x(-7.6):.1f}" y2="{Z(0):.1f}"/>')
    # right: blade height
    d.dim_v_text(zt - BLADE_UP, zt, d.x(A + KERF) + 170, f"blade {frac(BLADE_UP)} = tenon length",
                 pxo=d.x(A + KERF))
    # below the table: t, cheek offset, then base and shim stack
    y0 = Z(0) + TT * K
    d.dim_h_small(SHIM, SHIM + T_STOCK, y0 + 24, f"t = {frac(T_STOCK)} stock", pyo=Z(0))
    d.dim_h_small(SHIM, A, y0 + 50, f"(t + T)/2 = {frac(CHEEK)} shim face to blade", pyo=Z(0))
    d.dim_h(-BASE_W, 0, y0 + 76, f"base {frac(BASE_W)} wide", pyo=Z(0), below=True)
    d.dim_h_small(0, SHIM, y0 + 76, f"s = {frac(SHIM)} shim stack", pyo=Z(0))
    d.text(d.x(-7.5), y0 + 106, f"Example: {frac(T_STOCK)} stock, {frac(T_TENON)} tenon: s = A − (t + T)/2 = "
           f"{frac(A)} − {frac(CHEEK)} = {frac(SHIM)}. The slot-to-blade distance is saw-dependent;", "n", "start")
    d.text(d.x(-7.5), y0 + 122, "the base's cross slots let you set A once. Light fill = handle and bracket seen beyond.",
           "n", "start")
    d.save(path, "Tenoning jig end view", EXTRA)


def plan(path):
    K = 24
    d = Drawing(620, 586, 300, 90, s=K)
    d.text(20, 24, "Plan view, jig in the miter slot — 1 in = 24 px", "h", "start")
    ym = BASE_L / 2
    # table region and miter slot
    d.add(f'<rect x="{d.x(-7.6):.1f}" y="{d.y(-0.4):.1f}" width="{11.6*K:.1f}" height="{(BASE_L+0.8)*K:.1f}" '
          f'fill="#f2f2f2" stroke="#999" stroke-dasharray="4 3"/>')
    d.rect(SLOT_X - SLOT_W / 2, -0.4, SLOT_X + SLOT_W / 2, BASE_L + 0.4, "tjs")
    d.text(d.x(SLOT_X), d.y(BASE_L + 0.4) + 13, "miter slot", "n")
    # base; runner under it (hidden) with its 6 nut pockets; centre pocket under the centre slot
    d.rect(-BASE_W, 0, 0, BASE_L, "face")
    r0 = ym - (RUN_POCKET0 + 2 * RUN_PITCH)
    d.rect(SLOT_X - RUN_W / 2, r0, SLOT_X + RUN_W / 2, r0 + RUN_L, "hid")
    for k in range(RUN_POCKETS):
        d.add(f'<circle class="hid" cx="{d.x(SLOT_X):.1f}" cy="{d.y(r0 + RUN_POCKET0 + k * RUN_PITCH):.1f}" r="4"/>')
    for yy in (ym - BSLOT_PITCH, ym, ym + BSLOT_PITCH):
        d.add(f'<rect x="{d.x(SLOT_X - BSLOT_L/2):.1f}" y="{d.y(yy - BSLOT_W/2):.1f}" width="{BSLOT_L*K:.1f}" '
              f'height="{BSLOT_W*K:.1f}" rx="{BSLOT_W/2*K:.1f}" fill="#fff" stroke="#333"/>')
    xl = d.x(SLOT_X + BSLOT_L / 2) + 6
    d.text(xl, d.y(3.4), "runner (dashed)", "n", "start")
    d.text(xl, d.y(6.1), "3 base slots", "n", "start")
    d.text(xl, d.y(6.1) + 14, f"{round(BSLOT_W * 32)}/32″ × {frac(BSLOT_L)}", "n", "start")
    # fence, brackets, handle
    d.rect(-FENCE_T, 0, 0, BASE_L, "wood")
    for yc in BR_Y:
        d.rect(-FENCE_T - BR_L, yc - BR_W / 2, -FENCE_T, yc + BR_W / 2, "spacer")
        d.line(-FENCE_T - BR_L, yc, -FENCE_T - BR_T, yc, "spacer")       # web
        d.leader(d.x(-FENCE_T - BR_L), d.y(yc), d.x(-FENCE_T - BR_L) - 12, d.y(yc), "bracket", "end")
    d.rect(HD_X - HD_FX / 2, HD_Y - HD_FY / 2, HD_X + HD_FX / 2, HD_Y + HD_FY / 2, "spacer")
    d.add(f'<circle class="spacer" cx="{d.x(HD_X):.1f}" cy="{d.y(HD_Y):.1f}" r="{HD_KNOB/2*K:.1f}"/>')
    d.text(d.x(HD_X), d.y(HD_Y + HD_FY / 2) + 13, "handle", "n")
    # shims (one footprint: the two stacks are one above the other), stock, blade
    xc = 0.0
    for p in shim_combo(SHIM):
        d.rect(xc, ym - SHIM_PLATE_L / 2, xc + p, ym + SHIM_PLATE_L / 2, "spacer")
        xc += p
    d.rect(SHIM, ym - STOCK_W / 2, SHIM + T_STOCK, ym + STOCK_W / 2, "shelf")
    d.add(f'<rect x="{d.x(A):.1f}" y="{d.y(-0.4):.1f}" width="{KERF*K:.1f}" height="{(BASE_L+0.8)*K:.1f}" fill="#444" opacity=".35"/>')
    xr = d.x(A + KERF) + 18
    d.text(xr, d.y(2.0), "blade plane", "n", "start")
    d.leader(d.x(SHIM / 2), d.y(ym - SHIM_PLATE_L / 2 + 0.15), xr - 3, d.y(4.6) - 4, f"shims, s = {frac(SHIM)}")
    d.leader(d.x(SHIM + T_STOCK), d.y(ym), xr - 3, d.y(ym) - 4, f"stock ({frac(STOCK_W)} wide shown)")
    d.text(xr, d.y(ym) + 14, "stands on the table, not the base", "n", "start")
    d.text(d.x(-6.8), d.y(-0.9), "feed ↓", "n", "start")
    # dims
    d.dim_h(-BASE_W, 0, d.y(-1.5), f"base {frac(BASE_W)}", pyo=d.y(0))
    d.dim_h(0, A, d.y(-1.5), f"A {frac(A)}", pyo=d.y(0))
    xs = d.x(SLOT_X - BSLOT_L / 2)
    px = d.x(-BASE_W) - 24
    for y1 in (ym - BSLOT_PITCH, ym):
        d.dim_v(y1, y1 + BSLOT_PITCH, px, f"{BSLOT_PITCH/MM:.0f} mm")
    for yy in (ym - BSLOT_PITCH, ym, ym + BSLOT_PITCH):
        d.add(f'<line class="ext" x1="{px:.1f}" y1="{d.y(yy):.1f}" x2="{xs:.1f}" y2="{d.y(yy):.1f}"/>')
    d.dim_v(0, ym, px - 26, f"{frac(ym)} to centre slot", pxo=d.x(-BASE_W))
    d.dim_v(0, BASE_L, px - 52, f"{frac(BASE_L)} long", pxo=d.x(-BASE_W))
    d.dim_h_small(-FENCE_T, 0, d.y(BASE_L + 0.4) + 22, f"fence {frac(FENCE_T)}", pyo=d.y(BASE_L), side="left")
    yl = d.y(BASE_L + 0.4) + 52
    d.text(20, yl, f"Grey = printed parts. Runner dashed under the base; ○ = its {RUN_POCKETS} nut pockets "
           f"({RUN_PITCH/MM:.0f} mm pitch).", "n", "start")
    d.text(20, yl + 16, f"The base slots sit over pockets 1, 3 and 5, {BSLOT_PITCH/MM:.0f} mm ≈ {BSLOT_PITCH:.2f}″ apart, "
           f"so the runner sits {(RUN_L / 2 - RUN_POCKET0 - 2 * RUN_PITCH) / MM:.0f} mm off centre.", "n", "start")
    d.text(20, yl + 32, "Brackets sit near each end; the handle is shown clear of the slots, place it to suit.",
           "n", "start")
    d.save(path, "Tenoning jig plan view", EXTRA)


def cuts(path):
    K = 110
    d = Drawing(980, 580, 0, 0, s=K)
    t, T, k, c, w = T_STOCK, T_TENON, KERF, CHEEK, WASTE
    zt, hs = 3.6, 2.6                           # table line; stock shown above it
    d.text(20, 24, "Cut sequence, looking along the feed — 1 in = 110 px (detail)", "h", "start")

    def stock(x0, solid_from=0.0, notch=None):
        """Stock outline with a break line on top; notch=(xa, xb) cuts a tenon."""
        top = zt - hs
        zz = [(x0 + t, top), (x0 + 0.75 * t, top - 0.06), (x0 + 0.5 * t, top + 0.04),
              (x0 + 0.25 * t, top - 0.06), (x0, top)]
        if notch:
            sh = zt - BLADE_UP
            low = [(x0, sh), (x0 + notch[0], sh), (x0 + notch[0], zt), (x0 + notch[1], zt),
                   (x0 + notch[1], sh), (x0 + t, sh)]
        else:
            low = [(x0, zt), (x0 + t, zt)]
        d.poly(low + zz, "shelf")

    def shims(x0):
        xc, top = x0 - SHIM, zt - 2.3
        for p in shim_combo(SHIM):
            d.rect(xc, top, xc + p, zt, "spacer")
            xc += p
        d.text(d.x(x0 - SHIM + 0.25), d.y(zt - 1.9), "shims", "n")

    def faces(x0, left, right):
        d.text(d.x(x0) + 6, d.y(zt - 2.05), left, "h", "start")
        d.text(d.x(x0 + t) - 6, d.y(zt - 2.05), right, "h", "end")

    def table(x0):
        d.rect(x0 - SHIM - 0.15, zt, x0 + t + 0.45, zt + 0.25, "tjt")

    def t_dim(x0):
        d.dim_h(x0, x0 + t, d.y(zt - hs) - 22, f"t = {frac(t)}", pyo=d.y(zt - hs))

    def cheek_dim(x0, py):           # label to the left, in the clear space under the shims
        d.dim_h(x0, x0 + c, py, "", pyo=d.y(zt))
        d.text(d.x(x0) - 6, py + 4, f"(t + T)/2 = {frac(c)}", "t", "end")

    r1, r2 = d.y(zt + 0.25) + 22, d.y(zt + 0.25) + 48
    # 1: first cheek, face A on the shims
    x0 = 0.95
    d.text(d.x(x0 - SHIM), 56, "1  Face A on the shims, first cheek", "t", "start")
    table(x0); shims(x0); stock(x0)
    d.rect(x0 + c + k, zt - BLADE_UP, x0 + t, zt, "tjw")
    d.rect(x0 + c, zt - BLADE_UP, x0 + c + k, zt, "tjk")
    faces(x0, "A", "B"); t_dim(x0)
    d.dim_h_small(x0 + c, x0 + c + k, r1, f"kerf {frac(k)}", pyo=d.y(zt))
    cheek_dim(x0, r2)
    d.dim_v(zt - BLADE_UP, zt, d.x(x0 + t) + 28, f"blade {frac(BLADE_UP)} = tenon length",
            pxo=d.x(x0 + c + k), left=False)
    # 2: turned end for end, face B on the shims
    x0 = 3.85
    d.text(d.x(x0 - SHIM), 56, "2  Turn end for end: face B on the shims", "t", "start")
    table(x0); shims(x0); stock(x0)
    d.rect(x0, zt - BLADE_UP, x0 + w - k, zt, "tjw")
    d.rect(x0 + c + k, zt - BLADE_UP, x0 + t, zt, "tjw")
    d.rect(x0 + w - k, zt - BLADE_UP, x0 + w, zt, "tjs")
    d.rect(x0 + c, zt - BLADE_UP, x0 + c + k, zt, "tjk")
    faces(x0, "B", "A"); t_dim(x0)
    xr = d.x(x0 + t) + 12
    d.leader(d.x(x0 + w - k / 2), d.y(zt - BLADE_UP), xr, d.y(zt - 2.25), "first kerf (from cut 1)")
    d.leader(d.x(x0 + c + k / 2), d.y(zt - BLADE_UP), xr, d.y(zt - 1.75), "second cut")
    d.dim_h_small(x0 + w, x0 + c, r1, f"T = {frac(T)} left between kerfs", pyo=d.y(zt))
    cheek_dim(x0, r2)
    # 3: shoulders cut on the crosscut sled
    x0 = 6.75
    d.text(d.x(x0) - 40, 56, "3  Shoulders on the crosscut sled", "t", "start")
    stock(x0, notch=(w, c))
    d.rect(x0, zt - BLADE_UP, x0 + w, zt, "hid")
    d.rect(x0 + c, zt - BLADE_UP, x0 + t, zt, "hid")
    faces(x0, "B", "A"); t_dim(x0)
    d.leader(d.x(x0 + (c + t) / 2), d.y(zt - BLADE_UP), d.x(x0 + t) + 12, d.y(zt - 2.05), "shoulder")
    d.leader(d.x(x0 + w / 2), d.y(zt - BLADE_UP), d.x(x0) - 12, d.y(zt - 2.05), "shoulder", "end")
    d.dim_h_small(x0, x0 + w, r1, f"{frac(w)}", pyo=d.y(zt), side="left")
    d.dim_h_small(x0 + c, x0 + t, r1, f"{frac(w)} = (t − T)/2", pyo=d.y(zt))
    d.dim_h(x0 + w, x0 + c, r2, f"T = {frac(T)}", pyo=d.y(zt), below=True)
    d.dim_v(zt - BLADE_UP, zt, d.x(x0 + t) + 28, f"tenon {frac(BLADE_UP)} long", pxo=d.x(x0 + c), left=False)
    # notes
    yn = r2 + 44
    d.text(20, yn, f"Shown: t = {frac(t)} stock, T = {frac(T)} tenon, {frac(k)} kerf, s = {frac(SHIM)} (A = {frac(A)}). "
           "The blade's near plane sits (t + T)/2 from the shim face on both cuts, so the kerf", "n", "start")
    d.text(20, yn + 16, "always lands in the waste and the tenon comes out centred and T thick whatever the kerf. "
           "Hatched = waste still attached; dark = blade; white = first kerf;", "n", "start")
    d.text(20, yn + 32, "dashed = waste freed by the shoulder cuts.", "n", "start")
    d.save(path, "Tenoning jig cut sequence", EXTRA)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "..", "static", "static", "woodworking")
    os.makedirs(out, exist_ok=True)
    end(os.path.join(out, "tenoning-jig-end.svg"))
    plan(os.path.join(out, "tenoning-jig-plan.svg"))
    cuts(os.path.join(out, "tenoning-jig-cuts.svg"))
    print("wrote 3 SVGs to", os.path.normpath(out))
