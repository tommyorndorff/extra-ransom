#!/usr/bin/env python3
"""True-scale SVGs for the miter-slot tenoning jig plan.

Usage: python3 tools/woodworking/tenoning_jig_drawings.py
Writes static/static/woodworking/tenoning-jig-{end,plan}.svg
Geometry in inches. X is across the saw (blade to the right), Y is the feed direction
in the plan view. A = blade's left plane to the fence face.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from modern_craftsman_drawings import Drawing

A = 1.25
BASE_T, FENCE_T = 0.75, 0.75
BASE_W, BASE_L = 7.0, 16.0
FENCE_H = 10.0
KERF = 0.125
BLADE_UP = 1.5                 # blade height above the table (= tenon length)
T_STOCK, T_TENON = 0.75, 0.375
SHIM = A - (T_STOCK + T_TENON) / 2   # 11/16
SLOT_W, SLOT_D = 0.75, 0.375
RUN_W, RUN_H = 0.733, 0.346
SLOT_X = -5.1                  # slot centre (saw-dependent; drawn typical)


def end(path):
    K = 34
    d = Drawing(900, 640, 330, 120, s=K)
    d.text(20, 24, "End view looking along the feed — 1 in = 34 px", "h", "start")
    ztab = 11.0                                   # table surface (y down)
    TB = ztab * K                                  # pixel y offset helper
    d.add(f'<rect x="{d.x(-7.6):.1f}" y="{d.y(ztab):.1f}" width="{11.4*K:.1f}" height="{1.3*K:.1f}" fill="#d9d9d9" stroke="#555" stroke-width="1.2"/>')
    d.text(d.x(3.6), d.y(ztab) + 1.3 * K - 6, "table", "n", "end")
    sx0 = SLOT_X - SLOT_W / 2
    d.add(f'<rect x="{d.x(sx0):.1f}" y="{d.y(ztab):.1f}" width="{SLOT_W*K:.1f}" height="{SLOT_D*K:.1f}" fill="#fff" stroke="#555" stroke-width="1.2"/>')
    d.rect(SLOT_X - RUN_W / 2, ztab, SLOT_X + RUN_W / 2, ztab + RUN_H, "spacer")    # runner
    d.rect(-BASE_W, ztab - BASE_T, 0, ztab, "face")
    d.rect(-FENCE_T, ztab - FENCE_H, 0, ztab - BASE_T, "wood")
    d.text(d.x(-3.6), d.y(ztab - BASE_T / 2) + 4, "base ¾″ ply", "n")
    d.text(d.x(-FENCE_T) - 8, d.y(ztab - 6.0), "fence ¾″ ply", "n", "end")
    d.rect(0, ztab - 7.5, SHIM, ztab, "spacer")
    d.rect(SHIM, ztab - 9.0, SHIM + T_STOCK, ztab, "shelf")
    d.text(d.x(SHIM + T_STOCK + 0.15), d.y(ztab - 2.5), "stock", "n", "start")
    d.text(d.x(SHIM / 2), d.y(ztab - 3.2), "shims", "n")
    d.add(f'<rect x="{d.x(A):.1f}" y="{d.y(ztab-BLADE_UP):.1f}" width="{KERF*K:.1f}" height="{BLADE_UP*K:.1f}" fill="#444" stroke="#222"/>')
    d.text(d.x(A + KERF + 0.3), d.y(ztab - 0.75), "blade (kerf)", "n", "start")
    # C-clamp: pads on fence back and stock face, frame arcs over the stock top
    cy, top = ztab - 8.2, ztab - 9.9
    xf, xs = d.x(-FENCE_T), d.x(SHIM + T_STOCK)
    xl, xr = d.x(-FENCE_T - 0.3), d.x(SHIM + T_STOCK + 0.3)
    d.add(f'<path d="M{xf:.1f},{d.y(cy):.1f} L{xl:.1f},{d.y(cy):.1f} L{xl:.1f},{d.y(top):.1f} L{xr:.1f},{d.y(top):.1f} L{xr:.1f},{d.y(cy):.1f} L{xs:.1f},{d.y(cy):.1f}" fill="none" stroke="#1f5fa8" stroke-width="3"/>')
    d.text((xl + xr) / 2, d.y(top) - 8, "C-clamp: fence back to stock face, above the blade", "n")
    # dims
    d.dim_h(0, A, 62, "A = 1¼″ blade's left plane to fence", pyo=d.y(ztab - BLADE_UP))
    d.dim_h(-BASE_W, 0, d.y(ztab) + 1.3 * K + 22, "base 7″ wide", pyo=d.y(ztab), below=True)
    d.dim_h(0, SHIM, d.y(ztab) + 1.3 * K + 22, "s = 11/16″ of shims", pyo=d.y(ztab), below=True)
    d.dim_h(SHIM, A, d.y(ztab) + 1.3 * K + 48, "cheek 9/16″ from stock face", pyo=d.y(ztab), below=True)
    d.dim_v(ztab - BLADE_UP, ztab, d.x(A) + 170, "blade ≈ 1½″ above table", pxo=d.x(A + KERF))
    d.text(d.x(-7.5), d.y(ztab) + 1.3 * K + 82, "Example: ¾″ stock, ⅜″ tenon: s = A − (t + T)/2 = 1¼ − 9/16 = 11/16″. The slot-to-blade distance is saw-dependent;", "n", "start")
    d.text(d.x(-7.5), d.y(ztab) + 1.3 * K + 98, "the runner is slotted in the base so you can set A once.", "n", "start")
    d.save(path, "Tenoning jig end view")


def plan(path):
    K = 24
    d = Drawing(960, 500, 300, 90, s=K)
    d.text(20, 24, "Plan view, jig in the miter slot — 1 in = 24 px", "h", "start")
    # y runs along feed: draw feed axis downward as +y
    def R(x1, y1, x2, y2, cls):
        d.rect(x1, y1, x2, y2, cls)
    # table region
    d.add(f'<rect x="{d.x(-7.6):.1f}" y="{d.y(-0.4):.1f}" width="{11.6*K:.1f}" height="{(BASE_L+0.8)*K:.1f}" fill="#f2f2f2" stroke="#999" stroke-dasharray="4 3"/>')
    # slot
    d.add(f'<rect x="{d.x(SLOT_X-SLOT_W/2):.1f}" y="{d.y(-0.4):.1f}" width="{SLOT_W*K:.1f}" height="{(BASE_L+0.8)*K:.1f}" fill="#fff" stroke="#555"/>')
    # base, runner (hidden, dashed)
    R(-BASE_W, 0, 0, BASE_L, "face")
    d.add(f'<rect class="hid" x="{d.x(SLOT_X-RUN_W/2):.1f}" y="{d.y(8.0-4.725):.1f}" width="{RUN_W*K:.1f}" height="{9.45*K:.1f}"/>')
    # runner screw slots (across the base)
    for yy in (8.0 - 3.15, 8.0, 8.0 + 3.15):
        d.add(f'<rect x="{d.x(SLOT_X-0.7):.1f}" y="{d.y(yy)-3:.1f}" width="{1.4*K:.1f}" height="6" rx="3" fill="#fff" stroke="#333"/>')
    d.text(d.x(-6.8), d.y(15.4), "3 slots over runner nuts", "n", "start")
    # fence
    R(-FENCE_T, 0, 0, BASE_L, "wood")
    d.text(d.x(-FENCE_T / 2), d.y(BASE_L + 0.8), "fence", "n")
    # brackets (back of fence)
    for yy in (3.0, 13.0):
        d.add(f'<polygon class="leg" points="{d.x(-FENCE_T):.1f},{d.y(yy-1.6):.1f} {d.x(-FENCE_T-2.2):.1f},{d.y(yy):.1f} {d.x(-FENCE_T):.1f},{d.y(yy+1.6):.1f}"/>')
    d.text(d.x(-6.8), d.y(1.0), "printed fence brackets ▶", "n", "start")
    # shims + stock + blade
    R(0, 4.0, SHIM, 11.0, "spacer")
    R(SHIM, 3.5, SHIM + T_STOCK, 11.5, "shelf")
    d.add(f'<rect x="{d.x(A):.1f}" y="{d.y(-0.4):.1f}" width="{KERF*K:.1f}" height="{(BASE_L+0.8)*K:.1f}" fill="#444" opacity=".35"/>')
    d.text(d.x(A) + 22, d.y(2.0), "blade plane", "n", "start")
    d.text(d.x(A) + 22, d.y(7.5), "stock stands here", "n", "start")
    d.text(d.x(A) + 22, d.y(8.2), "(on the table, not the base)", "n", "start")
    d.text(d.x(-6.8), d.y(-0.9), "feed ↓", "n", "start")
    d.dim_h(-BASE_W, 0, d.y(-1.5), "base 7″", pyo=d.y(0))
    d.dim_h(0, A, d.y(-1.5), "A 1¼″", pyo=d.y(0))
    d.dim_v(0, BASE_L, d.x(-BASE_W) - 30, "16″ long", pxo=d.x(-BASE_W))
    d.save(path, "Tenoning jig plan view")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "..", "static", "static", "woodworking")
    os.makedirs(out, exist_ok=True)
    end(os.path.join(out, "tenoning-jig-end.svg"))
    plan(os.path.join(out, "tenoning-jig-plan.svg"))
    print("wrote 2 SVGs to", os.path.normpath(out))
