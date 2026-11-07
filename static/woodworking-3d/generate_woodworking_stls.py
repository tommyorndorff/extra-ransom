#!/usr/bin/env python3
"""
Parametric STL generator for the 3D-printed parts called for by the woodworking
plans (Adjustable Scarf Jig, DW745 Mobile Saw Cart). All dimensions in mm.
Parts are exported in print orientation.

Requirements:  pip install manifold3d trimesh numpy matplotlib
Usage:         python3 generate_woodworking_stls.py

Dimensions that depend on YOUR hardware (saw feet, saw dust port, hose) are in
the parameter block below and are estimates -- measure and regenerate.
"""
import math
import os
import numpy as np
from manifold3d import Manifold, CrossSection

HERE = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(HERE, "previews")
os.makedirs(PREVIEW_DIR, exist_ok=True)

SEG = 96
IN = 25.4

# -- scarf jig (from the plan) ---------------------------------------------
# Ratio gauge: step height = drop d at the 12" mark = 12 / ratio (inches)
RATIOS = [8, 10, 12, 16, 20, 23.3, 24, 30]
GAUGE_STEP_W = 12.0          # width of each step along the gauge
GAUGE_THICK = 10.0           # thickness (print-on-side: heights lie in the XY plane)
INSERT_PITCH = 2 * IN        # 1/4-20 insert pairs are 1" either side of centre -> 2" apart
HOLE_QT20 = 6.8              # clearance for a 1/4-20 bolt
HEX_QT20_AF = 11.6           # 1/4-20 hex head (11.1 across flats) + clearance
PEG_D = 6.0                  # peg that keys into a 1/4-20 threaded insert
PEG_H = 6.0

# -- saw cart (ESTIMATES: measure your saw, then regenerate) ---------------
FOOT_D = 40.0                # saw rubber foot diameter (est.)
FOOT_DEPTH = 14.0            # how deep the foot sits in the cup
SAW_PORT_OD = 64.5           # DW745 rear dust port (measured on one saw, per the plan)
HOSE_ID = 2.5 * IN           # 2-1/2" hose slips over the adapter spigot


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))

def cyl_z(h, d, seg=SEG):
    return Manifold.cylinder(h, d / 2, d / 2, seg)

def hexagon_z(depth, af):
    r = af / 2 / math.cos(math.radians(30))
    return Manifold.cylinder(depth, r, r, 6)


# ---------------------------------------------------------------------------
# Scarf jig parts
# ---------------------------------------------------------------------------

def part_ratio_gauge():
    """Stepped gauge. Stand it on the bed at the 12" line; the step for your
    ratio should just touch a straightedge laid across the rails. Printed on
    its side so step heights are exact; verify once with calipers."""
    m = None
    for i, r in enumerate(RATIOS):
        h = 12.0 / r * IN
        s = box(i * GAUGE_STEP_W, (i + 1) * GAUGE_STEP_W, 0, h, 0, GAUGE_THICK)
        m = s if m is None else m + s
    return m


def part_hold_down_bar():
    """3/4 x 3/4 x 3 bar, two 1/4-20 bolts 2" apart, pocket for a cork pad.
    Printed with the pad pocket facing up."""
    L, W, H = 3 * IN, 0.75 * IN, 0.75 * IN
    m = box(0, L, 0, W, 0, H)
    for dx in (-INSERT_PITCH / 2, INSERT_PITCH / 2):
        m -= cyl_z(H + 2, HOLE_QT20).translate((L / 2 + dx, W / 2, -1))
    m -= box(L / 2 - 30, L / 2 + 30, W / 2 - 7, W / 2 + 7, H - 1.6, H + 1)
    return m


def part_hold_down_knob():
    """Fluted knob. A 1/4-20 hex-head bolt drops head-first into the top pocket."""
    D, H = 32.0, 14.0
    m = cyl_z(H, D)
    for k in range(8):
        a = k * math.pi / 4
        m -= cyl_z(H + 2, 7.0, 48).translate(
            (D / 2 * math.cos(a), D / 2 * math.sin(a), -1))
    m -= cyl_z(H + 2, HOLE_QT20).translate((0, 0, -1))
    m -= hexagon_z(7.5, HEX_QT20_AF).translate((0, 0, H - 7.0))
    return m


def _fence(pegs):
    L = max(pegs) + 12.7
    T, Hh = 0.25 * IN, 0.5 * IN
    m = box(0, L, 0, T, 0, Hh)
    for x in pegs:
        m += cyl_z(PEG_H + 1, PEG_D, 48).translate((x, T / 2, Hh - 1))
    return m

def part_fence_pair():
    """Fence segment with two pegs on the 2" insert pitch."""
    return _fence([12.7, 12.7 + INSERT_PITCH])

def part_fence_single():
    """Fence end piece with one peg."""
    return _fence([12.7])


# ---------------------------------------------------------------------------
# DW745 saw cart parts
# ---------------------------------------------------------------------------

def part_turnbutton():
    """Pivots on a #10 screw; a quarter turn clamps the lift-off front panel."""
    L, W, T = 38.0, 12.0, 4.0
    m = box(W / 2, L - W / 2, 0, W, 0, T)
    m += cyl_z(T, W).translate((W / 2, W / 2, 0))
    m += cyl_z(T, W).translate((L - W / 2, W / 2, 0))
    m -= cyl_z(T + 2, 5.4, 48).translate((W / 2, W / 2, -1))
    return m


def part_wall_hook():
    """J-hook for fence / miter gauge / cord. Two countersunk screws."""
    X, Y, P = 60.0, 30.0, 6.0
    m = box(0, X, 0, Y, 0, P)
    m += box(0, 14, 0, Y, P - 0.01, 46)            # arm
    m += box(0, 34, 0, Y, 40, 46)                  # lip
    for x in (30, 52):
        m -= cyl_z(P + 2, 4.6, 48).translate((x, Y / 2, -1))
        m -= Manifold.cylinder(3.2, 4.6 / 2, 9.0 / 2, 48).translate((x, Y / 2, P - 3.2))
    return m


def part_foot_cup():
    """Cradles one of the saw's rubber feet; screws to a support rail."""
    wall, floor = 3.0, 3.0
    R_out = FOOT_D / 2 + wall
    m = cyl_z(floor, 70.0)
    m += cyl_z(FOOT_DEPTH + floor, 2 * R_out).translate((0, 0, 0))
    m -= cyl_z(FOOT_DEPTH + 1, FOOT_D).translate((0, 0, floor))
    for x in (-29.0, 29.0):
        m -= cyl_z(floor + 2, 4.6, 48).translate((x, 0, -1))
    return m


def part_rear_port_adapter():
    """Saw dust port -> 2-1/2" hose. Socket over the 64.5 mm port, spigot under the hose."""
    sock_od, sock_len = SAW_PORT_OD + 5.5, 28.0
    spig_od, spig_len = HOSE_ID - 1.0, 36.0
    cone = 12.0
    outer = cyl_z(sock_len, sock_od)
    outer += Manifold.cylinder(cone, sock_od / 2, spig_od / 2, SEG).translate((0, 0, sock_len))
    outer += cyl_z(spig_len, spig_od).translate((0, 0, sock_len + cone))
    total = sock_len + cone + spig_len
    outer -= cyl_z(sock_len, SAW_PORT_OD + 0.5).translate((0, 0, 0))
    outer -= cyl_z(total + 2, spig_od - 5.0).translate((0, 0, -1))
    # two retaining ribs on the spigot for the hose
    for z in (sock_len + cone + 10, sock_len + cone + 22):
        outer += Manifold.cylinder(2.0, spig_od / 2, spig_od / 2 + 1.2, SEG).translate((0, 0, z)) - \
                 cyl_z(2.2, spig_od - 5.0).translate((0, 0, z - 0.1))
    return outer


PARTS = {
    "ratio_gauge":       (part_ratio_gauge,       1),
    "hold_down_bar":     (part_hold_down_bar,     1),
    "hold_down_knob":    (part_hold_down_knob,    2),
    "fence_pair":        (part_fence_pair,        2),
    "fence_single":      (part_fence_single,      1),
    "turnbutton":        (part_turnbutton,        6),
    "wall_hook":         (part_wall_hook,         3),
    "foot_cup":          (part_foot_cup,          4),
    "rear_port_adapter": (part_rear_port_adapter, 1),
}


def to_trimesh(man):
    import trimesh
    mesh = man.to_mesh()
    return trimesh.Trimesh(
        vertices=np.asarray(mesh.vert_properties, dtype=np.float64),
        faces=np.asarray(mesh.tri_verts, dtype=np.int64),
        process=True,
    )


def render_preview(tm, name):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(projection="3d")
    pc = Poly3DCollection(tm.vertices[tm.faces], edgecolor="none")
    n = tm.face_normals
    light = np.array([0.4, -0.6, 0.7]); light /= np.linalg.norm(light)
    lum = np.clip(n @ light, 0, 1) * 0.7 + 0.3
    pc.set_facecolor(np.column_stack(
        [lum * 0.55, lum * 0.42, lum * 0.28, np.ones_like(lum)]))
    ax.add_collection3d(pc)
    lo, hi = tm.bounds
    c, r = (lo + hi) / 2, (hi - lo).max() / 2 * 1.1
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_axis_off(); ax.view_init(elev=28, azim=-55)
    fig.tight_layout(pad=0)
    fig.savefig(os.path.join(PREVIEW_DIR, f"{name}.png"), dpi=110,
                bbox_inches="tight", transparent=True)
    plt.close(fig)


def main():
    print(f"{'part':<18} {'qty':>3} {'tris':>6} {'vol cm3':>8} {'genus':>5}  "
          f"{'bbox (mm)':<26} watertight")
    ok = True
    for name, (fn, qty) in PARTS.items():
        man = fn()
        tm = to_trimesh(man)
        tm.apply_translation(-tm.bounds[0])
        bb = tm.bounds
        dims = " x ".join(f"{d:.1f}" for d in (bb[1] - bb[0]))
        wt = tm.is_watertight and tm.is_winding_consistent and tm.volume > 0
        ok &= wt
        print(f"{name:<18} {qty:>3} {len(tm.faces):>6} {tm.volume/1000:>8.1f} "
              f"{man.genus():>5}  {dims:<26} {'yes' if wt else 'NO <-- BAD'}")
        tm.export(os.path.join(HERE, f"{name}.stl"))
        render_preview(tm, name)
    print("\nAll parts watertight." if ok else "\nSOME PARTS FAILED VALIDATION")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
