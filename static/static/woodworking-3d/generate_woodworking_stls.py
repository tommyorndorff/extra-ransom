#!/usr/bin/env python3
"""
Parametric STL generator for the 3D-printed parts called for by the woodworking
plans (Adjustable Scarf Jig, DW745 Mobile Saw Cart) plus generic table-saw accessories
that fit any SawStop (standard 3/4" x 3/8" miter slot). All dimensions in mm.
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

# -- table saw (any SawStop: standard 3/4" x 3/8" miter slot) ---------------
SLOT_W, SLOT_D = 0.75 * IN, 0.375 * IN   # 19.05 x 9.525
RUNNER_CLEAR = 0.45          # runner is this much narrower than the slot (tune for your printer)
RUNNER_W = SLOT_W - RUNNER_CLEAR         # 18.6
RUNNER_H = SLOT_D - 0.7                  # 8.8 -- stays below the table surface
CRUSH_RIB = 0.35             # featherboard friction ribs, per side
M5_NUT_AF, M5_NUT_T = 8.3, 4.8           # M5 nut pocket for sled-runner screws
SETUP_HEIGHTS_IN = [1/8, 1/4, 3/8, 1/2, 5/8, 3/4, 7/8, 1.0]


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


# ---------------------------------------------------------------------------
# Table saw parts (model-agnostic)
# ---------------------------------------------------------------------------

def _extrude(points, h):
    return Manifold.extrude(CrossSection([np.array(points, dtype=float)]), h)


def part_featherboard():
    """Finger board on a friction-fit miter-slot runner. PROTOTYPE: friction only
    (crush ribs); test-fit in a scrap slot and tune RUNNER_CLEAR / CRUSH_RIB.
    Printed upside down: fingers stand as vertical walls, runner points up."""
    L_base, W_base, H = 150.0, 24.0, 25.0
    m = box(0, L_base, 0, W_base, 0, H)
    pitch, n, flen, ft = 12.0, 10, 85.0, 3.2
    for i in range(n):
        f = box(0, ft, 0, flen, 0, H).rotate((0, 0, -30.0))     # leans 30 deg toward the feed
        m += f.translate((10 + i * pitch, W_base - 1.0, 0))
    run_len = 70.0
    x0 = L_base / 2 - run_len / 2
    ry0 = W_base / 2 - RUNNER_W / 2
    m += box(x0, x0 + run_len, ry0, ry0 + RUNNER_W, H - 0.01, H + RUNNER_H)
    for side in (ry0 - CRUSH_RIB, ry0 + RUNNER_W):
        m += box(x0, x0 + run_len, side, side + CRUSH_RIB, H + 2.0, H + RUNNER_H - 1.5)
    return m


def part_push_block():
    """Heel-and-toe push block. L-profile with an 8 mm heel that catches the back of the
    stock and a raised grip. Print on its side (profile flat on the bed). Fit a 1/8"
    rubber pad in the underside pocket."""
    prof = [(0, -8), (14, -8), (14, 0), (150, 0), (150, 12), (112, 12), (104, 58),
            (46, 58), (38, 12), (0, 12)]
    m = _extrude(prof, 85.0)
    m -= box(20, 145, -0.5, 1.0, 6, 79)       # pad pocket on the underside
    return m


def part_push_stick():
    """Narrow-rip push stick: wide handle, slim shaft, and a hook that catches the
    back of the stock. Printed with the hook pointing up."""
    plan = [(0, 0), (250, 0), (250, 32), (90, 32), (60, 55), (0, 55)]
    m = _extrude(plan, 13.0)
    m -= cyl_z(15, 24.0).translate((38, 27.5, -1))        # finger hole
    m += box(236, 250, 0, 32, 12.99, 13 + 15)              # hook (down in use)
    return m


def part_setup_steps():
    """Stepped depth blocks, 1/8" to 1" in 1/8" steps: set blade height or dado depth
    by comparing the blade to a step with a straightedge. Print on its side."""
    m = None
    for i, hin in enumerate(SETUP_HEIGHTS_IN):
        s = box(i * 14.0, (i + 1) * 14.0, 0, hin * IN, 0, 20.0)
        m = s if m is None else m + s
    return m


def part_angle_checker():
    """90/45 degree triangle for checking blade angle against the table, 100 mm legs."""
    m = _extrude([(0, 0), (100, 0), (0, 100)], 6.0)
    m -= cyl_z(8, 6.0).translate((16, 16, -1))              # hang hole
    return m


def part_sled_runner():
    """Miter-slot runner segment for a crosscut sled: clearance fit, 6 M5 nut pockets."""
    L = 240.0
    m = box(0, L, 0, RUNNER_W, 0, RUNNER_H)
    for k in range(6):
        x = 20 + k * 40
        m -= cyl_z(RUNNER_H + 2, 5.5, 48).translate((x, RUNNER_W / 2, -1))
        m -= hexagon_z(M5_NUT_T, M5_NUT_AF).translate((x, RUNNER_W / 2, -0.01))
    return m


# ---------------------------------------------------------------------------
# Tenoning jig parts
# ---------------------------------------------------------------------------

def part_tenon_shims():
    """Five spacer plates, 1/16" 1/8" 1/4" 1/2" 1/2", laid out on one bed. Stack them
    between the fence and the stock (any 1/16" step from 0 to 1-7/16"). Print flat so
    the thickness is set by layer count; verify each with calipers."""
    thick = [IN / 16, IN / 8, IN / 4, IN / 2, IN / 2]
    pw, pl, gap = 110.0, 70.0, 6.0
    m = None
    for i, t in enumerate(thick):
        col, row = i % 2, i // 2
        x, y = col * (pw + gap), row * (pl + gap)
        p = box(x, x + pw, y, y + pl, 0, t)
        p -= cyl_z(t + 2, 12.0, 48).translate((x + pw - 18, y + pl / 2, -1))   # pull hole
        m = p if m is None else m + p
    return m


def part_jig_bracket():
    """Right-angle bracket with a web: squares the fence to the jig base. Two
    countersunk-ready screw holes per flange. Print on the base flange."""
    L, Wd, T, H = 60.0, 40.0, 6.0, 60.0
    m = box(0, L, 0, Wd, 0, T)                       # base flange
    m += box(0, T, 0, Wd, 0, H)                      # fence flange
    web = _extrude([(T - 0.01, T - 0.01), (L, T - 0.01), (T - 0.01, H)], 6.0)   # in XY -> map to XZ
    web = web.rotate((90, 0, 0)).translate((0, Wd / 2 + 3.0, 0))
    m += web
    for y in (8.0, Wd - 8.0):
        m -= cyl_z(T + 2, 4.6, 48).translate((40.0, y, -1))
        m -= cyl_z(T + 2, 4.6, 48).rotate((0, 90, 0)).translate((-1, y, 40.0))
    return m


def part_jig_handle():
    """Push handle for the jig: flange with two screw holes, a post and a rounded top."""
    m = box(0, 60, 0, 40, 0, 8)
    m += cyl_z(70.0, 28.0).translate((30, 20, 0))
    m += Manifold.sphere(18.0, 48).translate((30, 20, 70.0))
    for x in (12.0, 48.0):
        m -= cyl_z(10, 4.6, 48).translate((x, 20, -1))
    return m


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
    "featherboard":      (part_featherboard,      1),
    "push_block":        (part_push_block,        2),
    "push_stick":        (part_push_stick,        2),
    "setup_steps":       (part_setup_steps,       1),
    "angle_checker":     (part_angle_checker,     1),
    "sled_runner":       (part_sled_runner,       4),
    "tenon_shims":       (part_tenon_shims,       2),
    "jig_bracket":       (part_jig_bracket,       2),
    "jig_handle":        (part_jig_handle,        1),
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
