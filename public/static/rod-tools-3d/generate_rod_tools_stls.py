#!/usr/bin/env python3
"""
Parametric STL generator for 3D-printable bamboo-rodmaking shop tools.
Each tool maps to a step of the build process documented on the Morgan
Hand Mill page. See the project page for what each tool does.

Requirements:  pip install manifold3d trimesh numpy matplotlib
Usage:         python3 generate_rod_tools_stls.py
"""
import math
import os
import numpy as np
from manifold3d import Manifold, CrossSection

HERE = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(HERE, "previews")
os.makedirs(PREVIEW_DIR, exist_ok=True)

SEG = 128
SEG_SM = 64

# ── shared hardware sizes ────────────────────────────────────────────────
HOLE_M4 = 4.5
HOLE_M8 = 8.4
CB_M4 = 8.8
HEX_M4_AF = 7.3
HEX_M8_AF = 13.4
INDICATOR_STEM_D = 9.6      # 3/8" dial indicator stem
FERRULE_BORE = 7.0          # example ferrule OD - regenerate for yours
PVC_OD = 48.6               # 1.5" sch40 dip tube + clearance


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))

def cyl_z(h, d, seg=SEG_SM):
    return Manifold.cylinder(h, d / 2, d / 2, seg)

def cyl_x(h, d, seg=SEG_SM):
    return cyl_z(h, d, seg).rotate((0, 90, 0))

def cyl_y(h, d, seg=SEG_SM):
    return cyl_z(h, d, seg).rotate((-90, 0, 0))

def hexagon_z(depth, af):
    r = af / 2 / math.cos(math.radians(30))
    return Manifold.cylinder(depth, r, r, 6)


# ──────────────────────────────────────────────────────────────────────────
# 1. Depth-gauge base: rides the flats of steel planing forms; a 3/8"-stem
# dial indicator clamps in the bore, its 60-deg point reading strip depth
# in the form groove. Slit + cross-bolt pinches the stem.
# ──────────────────────────────────────────────────────────────────────────

def part_depth_gauge_base():
    m = box(-35, 35, -20, 20, 0, 22)
    m -= cyl_z(24, INDICATOR_STEM_D, SEG).translate((0, 0, -1))
    # relief so only the two end pads ride the form (flat, self-cleaning)
    m -= box(-24, 24, -21, 21, -0.01, 1.5)
    # pinch slit from the front face to the bore; an M4 x 35 spans it:
    # socket head in a deep access tunnel on the +x side, nut in a
    # top-loaded hex track on the -x side (drops in from above)
    m -= box(-1.1, 1.1, -21, 0, 5, 23)
    m -= cyl_x(60, HOLE_M4).translate((-22, -12, 14))
    m -= cyl_x(29, CB_M4).translate((8, -12, 14))
    hexnut = hexagon_z(3.4, HEX_M4_AF).rotate((0, 90, 0)).translate((-12.3, -12, 14))
    m -= hexnut
    m -= box(-12.3, -8.9, -12 - HEX_M4_AF / 2, -12 + HEX_M4_AF / 2, 14, 23)
    return m


# ──────────────────────────────────────────────────────────────────────────
# 2. Node-sanding jig: holds a strip enamel-down over a disc sander so
# nodes sand flush without dishing. The tapered wedge presses in beside
# the strip and friction-locks it - no hardware at all.
# ──────────────────────────────────────────────────────────────────────────

def part_node_sanding_jig():
    m = box(0, 90, -15, 15, 0, 20)
    m -= box(-1, 91, -4.1, 4.1, 14, 21)          # 8.2 wide strip+wedge channel
    return m


def part_node_jig_wedge():
    """Tapered locking bar: 8 -> 4 mm over 120 mm; press in beside the
    strip until snug."""
    prof = CrossSection([[(0, 0), (120, 0), (120, 4.0), (0, 8.0)]])
    return prof.extrude(5.6).rotate((90, 0, 0)).translate((0, 2.8, 0))


# ──────────────────────────────────────────────────────────────────────────
# 3. Binding-cord spool caddy: bench-standing payoff for the bulk spool
# with a hole for a 1/8" brass fly-off arm (the Garrison article's
# shock-absorber trick).
# ──────────────────────────────────────────────────────────────────────────

def part_spool_caddy():
    m = box(0, 110, -30, 30, 0, 10)                       # base
    for x in (10, 100):
        up = box(x - 8, x + 8, -30, 30, 10, 75)
        up -= cyl_x(20, 8.6).translate((x - 10, 0, 55))   # axle seat
        # drop-in slot opens across the upright so a loaded axle lowers in
        up -= box(x - 9, x + 9, -4.3, 4.3, 55, 76)
        m += up
    m -= cyl_z(80, 3.5).translate((55, 22, -1))           # brass-rod socket
    for x, y in ((30, -20), (80, -20), (30, 20), (80, 20)):
        m -= cyl_z(12, HOLE_M4).translate((x, y, -1))
        m -= cyl_z(8, CB_M4).translate((x, y, 4))
    return m


# ──────────────────────────────────────────────────────────────────────────
# 4. Cork press: pressure discs + wing knobs for gluing a grip's cork
# rings on M8 threaded rod (press the grip off-rod, then ream and glue).
# ──────────────────────────────────────────────────────────────────────────

def part_cork_press_disc():
    m = cyl_z(8.0, 60.0, SEG)
    m -= cyl_z(10, HOLE_M8).translate((0, 0, -1))
    return m

def part_cork_press_knob():
    m = cyl_z(15.0, 40.0, SEG)
    for i in range(6):
        a = math.radians(60 * i)
        m -= cyl_z(17, 11.0, SEG_SM) \
            .translate((23 * math.cos(a), 23 * math.sin(a), -1))
    m -= cyl_z(17, HOLE_M8).translate((0, 0, -1))
    m -= hexagon_z(7.0, HEX_M8_AF).translate((0, 0, 15.0 - 7.0))
    return m


# ──────────────────────────────────────────────────────────────────────────
# 5. Finishing V-stand (print 2+): tall felt-lined V supports for turning
# a blank during wrap finishing and varnish work.
# ──────────────────────────────────────────────────────────────────────────

def part_finishing_v_stand():
    m = box(-40, 40, -25, 25, 0, 8)                       # foot
    m += box(-40, 40, -4, 4, 0, 120)                      # upright
    # 90-deg V opening upward across the 80 mm width, 25 deep
    vg = CrossSection([[(-26, 1), (0, -25), (26, 1)]]) \
        .extrude(10).rotate((90, 0, 0)).translate((0, 5, 120))
    m -= vg
    for x in (-28, 28):
        m -= cyl_z(10, HOLE_M4).translate((x, 14, -1))
        m -= cyl_z(6, CB_M4).translate((x, 14, 3.5))
    return m


# ──────────────────────────────────────────────────────────────────────────
# 6. Ferrule slitting collar: slips over the ferrule tang; 6 slots guide a
# jeweler's saw for even serrations. Regenerate FERRULE_BORE per ferrule.
# ──────────────────────────────────────────────────────────────────────────

def part_ferrule_slit_collar():
    m = cyl_z(14.0, FERRULE_BORE + 9.0, SEG)
    m -= cyl_z(16, FERRULE_BORE, SEG).translate((0, 0, -1))
    # saw slots stop 4 mm above the base so a solid band keeps the collar
    # in one piece; the saw bottoms out on the band, giving even cut depth
    for i in range(6):
        slot = box(-0.35, 0.35, 0, (FERRULE_BORE + 12) / 2, 4, 15) \
            .rotate((0, 0, 60 * i))
        m -= slot
    return m


# ──────────────────────────────────────────────────────────────────────────
# 7. Dip-tube dust cap: caps a 1.5" PVC varnish dip tube; centre hole
# passes the hanging wire so blanks can drip dust-free.
# ──────────────────────────────────────────────────────────────────────────

def part_dip_cap():
    # modelled pocket-up so it prints with zero overhang (flip to fit tube)
    m = cyl_z(20.0, PVC_OD + 8.0, SEG)
    m -= cyl_z(13.01, PVC_OD, SEG).translate((0, 0, 7.0))
    m -= cyl_z(22, 10.0, SEG_SM).translate((0, 0, -1))
    return m


# ──────────────────────────────────────────────────────────────────────────
# 8. Strip-sanding plate: a 60-deg V-channel the length of the plate. The
# strip's beveled (pith-side) point drops into the channel; the enamel
# face sits proud above the rails on either side. Run a flat sanding
# board over the top - once it rides the rails flush, the enamel face is
# level along the full length. Regenerate GROOVE_D for wider strips.
# ──────────────────────────────────────────────────────────────────────────

def part_strip_sanding_plate():
    length, width, thick = 250.0, 32.0, 14.0
    groove_d = 9.0                        # vertical channel depth
    half_angle = math.radians(30)         # half of the 60-deg included angle
    m = box(0, length, -width / 2, width / 2, 0, thick)
    vertex_z = thick - groove_d
    overshoot = 2.0                       # pokes through the top face for a clean cut
    top_z = thick + overshoot
    top_half = (top_z - vertex_z) * math.tan(half_angle)
    prof = CrossSection([[(-top_z, -top_half), (-vertex_z, 0), (-top_z, top_half)]])
    vg = prof.extrude(length + 4).rotate((0, 90, 0)).translate((-2, 0, 0))
    m -= vg
    return m


# ──────────────────────────────────────────────────────────────────────────

PARTS = {
    "depth_gauge_base":    (part_depth_gauge_base,    1),
    "node_sanding_jig":    (part_node_sanding_jig,    1),
    "node_jig_wedge":      (part_node_jig_wedge,      1),
    "spool_caddy":         (part_spool_caddy,         1),
    "cork_press_disc":     (part_cork_press_disc,     2),
    "cork_press_knob":     (part_cork_press_knob,     2),
    "finishing_v_stand":   (part_finishing_v_stand,   2),
    "ferrule_slit_collar": (part_ferrule_slit_collar, 1),
    "dip_cap":             (part_dip_cap,             1),
    "strip_sanding_plate": (part_strip_sanding_plate, 1),
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
        [lum * 0.35, lum * 0.65, lum * 0.45, np.ones_like(lum)]))
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
    print(f"{'part':<20} {'tris':>6} {'vol cm3':>8} {'genus':>5}  "
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
        print(f"{name:<20} {len(tm.faces):>6} {tm.volume/1000:>8.1f} "
              f"{man.genus():>5}  {dims:<26} {'yes' if wt else 'NO <-- BAD'}")
        tm.export(os.path.join(HERE, f"{name}.stl"))
        render_preview(tm, name)
    print("\nAll parts watertight." if ok else "\nSOME PARTS FAILED VALIDATION")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
