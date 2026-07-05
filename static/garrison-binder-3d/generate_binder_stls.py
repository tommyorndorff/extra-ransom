#!/usr/bin/env python3
"""
Parametric STL generator for a 3D-printed Garrison-style rod binder.

Architecture follows E. Garrison's binder as documented in Chris Bogart's
"Unlocking the Mysteries of the Garrison Binder" (see garrison-binder page):
a vertical face board, cradle on the top edge with a gap for the drive belt,
guide wheels + drive wheel on the face, a weight riding the belt's slack
loop, and a disc-drag cord tensioner.

Every rotating part takes two 608 bearings (8 x 22 x 7 mm skateboard
bearings). All mounting holes, counterbores, hex pockets, and adjustment
slots are printed in place - no post-print drilling.

Requirements:  pip install manifold3d trimesh numpy matplotlib
Usage:         python3 generate_binder_stls.py
Output:        ./<part>.stl + ./previews/<part>.png next to this script.

Tune the PARAMETERS block for your hardware (board thickness, bearing fit)
and re-run.
"""
import math
import os
import numpy as np
from manifold3d import Manifold, CrossSection

HERE = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(HERE, "previews")
os.makedirs(PREVIEW_DIR, exist_ok=True)

SEG = 128          # circular segments for wheels
SEG_SM = 64        # circular segments for small features

# ──────────────────────────────────────────────────────────────────────────
# PARAMETERS - tune for your hardware, then re-run
# ──────────────────────────────────────────────────────────────────────────

BOARD_T = 18.0          # face board thickness (3/4" ply = 18-19; measure yours)
BOARD_FIT = 0.35        # clearance added to board channels/slots

# 608 bearing (8 x 22 x 7). POCKET_D is a light press fit for a well-tuned
# FDM printer; if bearings fall out, reduce to 22.05; if they won't seat,
# raise to 22.25.
BEARING_OD = 22.0
POCKET_D = 22.15
POCKET_DEPTH = 7.1
WHEEL_BORE = 16.0       # clearance bore between pockets (clears inner race)
AXLE_D = 8.0            # M8 axles
HOLE_M8 = 8.4
HOLE_M5 = 5.5
HOLE_M4 = 4.5
HOLE_M4_TAP = 3.6       # self-tap pilot for M4 screws
CB_M4 = 8.8             # counterbore for M4 pan/button head
CB_M5 = 12.0            # counterbore for M5 head (fits an 8 mm socket too)
CRANK_BCD_R = 17.5      # crank bolt circle radius on the drive wheel face
HEX_M5_AF = 8.3         # across-flats pocket for M5 nut / hex head (8.0 nominal)

# Belt: 3/16" (4.8 mm) braided mason line, spliced into a loop
BELT_D = 4.8
GROOVE_DEPTH = 7.5      # deep groove per the Garrison article
GROOVE_ROOT_W = 2.0     # flat at groove root
GROOVE_HALF_ANGLE = 45  # 90 deg included V: flanks print support-free at 45 deg

# Wheels
DRIVE_OD = 64.0
IDLER_OD = 40.0
WHEEL_W = 20.0

# Cradle (per the article: ~1" trough, 3/16-1/4" gap between halves)
TROUGH_R = 12.7          # 1" diameter rod trough
CRADLE_LEN = 30.0        # each block's length along the rod axis
CRADLE_GAP = 5.0         # belt gap between the two blocks (set at assembly)
CHANNEL_DEPTH = 15.0     # how far the cradle straddles down over the board
# Belt plane offset: wheels stand off the board front face by a washer
# (2 mm), so the groove centre sits WASHER + WHEEL_W/2 in front of the face.
WASHER_T = 2.0
BELT_PLANE = WASHER_T + WHEEL_W / 2      # 12.0 mm in front of board face
TROUGH_ABOVE_EDGE = 19.3                 # trough bottom above board top edge

# Feed supports (article: 1-3/4" trough, bottoms level with cradle trough)
FEED_TROUGH_R = 22.25    # 1.75" diameter
DOWEL_D = 25.4           # 1" hardwood dowel posts
DOWEL_FIT = 0.35

# ──────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────

def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))

def cyl_z(h, d, seg=SEG_SM):
    """Cylinder along +Z from z=0."""
    return Manifold.cylinder(h, d / 2, d / 2, seg)

def cyl_x(h, d, seg=SEG_SM):
    """Cylinder along +X from x=0."""
    return cyl_z(h, d, seg).rotate((0, 90, 0))

def cyl_y(h, d, seg=SEG_SM):
    """Cylinder along +Y from y=0."""
    return cyl_z(h, d, seg).rotate((-90, 0, 0))

def hex_pocket_y(depth, af, seg_rot=0):
    """Hex prism along +Y from y=0, af = across flats."""
    r = af / 2 / math.cos(math.radians(30))
    h = Manifold.cylinder(depth, r, r, 6).rotate((-90, 0, seg_rot))
    return h

def slot_y(x0, x1, z_c, hole_d, y0, y1):
    """Slot along X (elongated hole), bored through in Y from y0 to y1."""
    l = y1 - y0
    a = cyl_y(l, hole_d).translate((x0, y0, z_c))
    b = cyl_y(l, hole_d).translate((x1, y0, z_c))
    mid = box(x0, x1, y0, y1, z_c - hole_d / 2, z_c + hole_d / 2)
    return a + b + mid

def hex_track_y(x0, x1, af, z_c, y0, y1):
    """Elongated hex-nut track: nut slides along X, flats at top/bottom."""
    l = y1 - y0
    a = hex_pocket_y(l, af, 0).translate((x0, y0, z_c))
    b = hex_pocket_y(l, af, 0).translate((x1, y0, z_c))
    mid = box(x0, x1, y0, y1, z_c - af / 2, z_c + af / 2)
    return a + b + mid


# ──────────────────────────────────────────────────────────────────────────
# Wheels
# ──────────────────────────────────────────────────────────────────────────

def belt_groove_cutter(rim_r, z_center):
    """Revolved V-groove cutter: 60 deg included, flat root, deep flanges."""
    t = math.tan(math.radians(GROOVE_HALF_ANGLE))
    root_r = rim_r - GROOVE_DEPTH
    over = 2.0                       # cutter extends past the rim
    hw_root = GROOVE_ROOT_W / 2
    hw_rim = hw_root + (GROOVE_DEPTH + over) * t
    prof = CrossSection([[
        (root_r, z_center - hw_root),
        (rim_r + over, z_center - hw_rim),
        (rim_r + over, z_center + hw_rim),
        (root_r, z_center + hw_root),
    ]])
    return prof.revolve(SEG)

def bearing_pockets(width):
    """Two 608 pockets w/ 0.8mm lead-in chamfers + clearance bore between."""
    pr = POCKET_D / 2
    cut = cyl_z(POCKET_DEPTH + 0.01, POCKET_D, SEG).translate((0, 0, -0.005))
    cut += Manifold.cylinder(0.8, pr + 0.8, pr, SEG)            # bottom chamfer
    top = cyl_z(POCKET_DEPTH + 0.01, POCKET_D, SEG) \
        .translate((0, 0, width - POCKET_DEPTH - 0.005))
    top += Manifold.cylinder(0.8, pr, pr + 0.8, SEG) \
        .translate((0, 0, width - 0.8))
    bore = cyl_z(width + 2, WHEEL_BORE, SEG).translate((0, 0, -1))
    return cut + top + bore

def make_wheel(od, width, crank_holes=False):
    r = od / 2
    w = Manifold.cylinder(width, r, r, SEG)
    w -= belt_groove_cutter(r, width / 2)
    w -= bearing_pockets(width)
    if crank_holes:
        # M4 self-tap pilots: the crank screws thread 17 mm into the wheel
        # from the arm side, so nothing protrudes from the wheel's back face
        # (which spins 2 mm in front of the board).
        for i in range(4):
            a = math.radians(90 * i)          # 0/90/180/270: opposite pairs
            x, y = CRANK_BCD_R * math.cos(a), CRANK_BCD_R * math.sin(a)
            w -= cyl_z(width + 2, HOLE_M4_TAP).translate((x, y, -1))
    return w

def part_drive_wheel():
    return make_wheel(DRIVE_OD, WHEEL_W, crank_holes=True)

def part_idler_wheel():
    return make_wheel(IDLER_OD, WHEEL_W)

def part_bearing_spacer():
    """Inner-race spacer: clamps between the two bearings' inner races so
    the axle nut can be fully tightened without pinching the outer races."""
    web = WHEEL_W - 2 * POCKET_DEPTH
    length = web + 0.3
    return cyl_z(length, 11.0, SEG_SM) - cyl_z(length + 2, 8.4, SEG_SM).translate((0, 0, -1))


# ──────────────────────────────────────────────────────────────────────────
# Cradle block (print 2) - straddles the board top edge, M5 clamp bolt in
# slotted holes so the pair slides to set the belt gap. Trough axis sits
# BELT_PLANE (12 mm) in front of the board face so the rod is centred in
# the belt plane. The gap-facing bottom edges of the trough slab carry 45
# degree relief chamfers so the belt can depart at less than 170 degrees
# of rod wrap without scraping the slab (the article's first-wheel rule).
#
# Part frame: X = rod axis (0..CRADLE_LEN), Y = 0 at board FRONT face
# (channel behind at -BOARD_T-fit..0), Z = 0 at part bottom; board top edge
# at Z = CHANNEL_DEPTH.
# ──────────────────────────────────────────────────────────────────────────

def part_cradle_block():
    ch_w = BOARD_T + BOARD_FIT
    back = -ch_w - 8.0               # 8 mm back cheek
    clamp_top = CHANNEL_DEPTH + 5.0
    trough_y = BELT_PLANE            # trough axis fwd of board face
    trough_bot = CHANNEL_DEPTH + TROUGH_ABOVE_EDGE
    top = trough_bot + TROUGH_R      # trough axis height = slab top
    front = trough_y + TROUGH_R + 4.3

    clamp = box(0, CRADLE_LEN, back, 10.0, 0, clamp_top)
    slab = box(0, CRADLE_LEN, back, front, clamp_top, top)
    m = clamp + slab

    # board channel
    m -= box(-1, CRADLE_LEN + 1, -ch_w, 0, -1, CHANNEL_DEPTH)
    # rod trough
    m -= cyl_x(CRADLE_LEN + 4, TROUGH_R * 2, SEG) \
        .translate((-2, trough_y, top))
    # 45 deg belt-relief chamfers on the slab's gap-facing bottom edges:
    # a diamond prism (square rotated 45 about Y) centred on each edge cuts
    # a chamfer with ~9 mm legs so the departing belt clears the slab.
    ch = 6.5
    wedge = box(-ch, ch, -(front - back) / 2 - 1, (front - back) / 2 + 1,
                -ch, ch).rotate((0, 45, 0)) \
        .translate((0, (back + front) / 2, 0))
    m -= wedge.translate((0, 0, clamp_top))
    m -= wedge.translate((CRADLE_LEN, 0, clamp_top))
    # clamp bolt: slotted through both cheeks (block slides +/-4.5 mm),
    # counterbore on the front face, captive-nut track on the back face
    zc = CHANNEL_DEPTH / 2
    xs0, xs1 = CRADLE_LEN / 2 - 4.5, CRADLE_LEN / 2 + 4.5
    m -= slot_y(xs0, xs1, zc, HOLE_M5, back - 1, 11)
    m -= slot_y(xs0, xs1, zc, CB_M5, 6.0, 11)                 # front cb, 4 mm web
    m -= hex_track_y(xs0, xs1, HEX_M5_AF, zc, back - 0.01, back + 4.5)
    return m


# ──────────────────────────────────────────────────────────────────────────
# Feed supports: printed head + printed base, joined by a user-cut 1" dowel
# so the trough height can match any bench/board setup.
# ──────────────────────────────────────────────────────────────────────────

def part_feed_head():
    W, D, H = 40.0, 56.0, 50.0
    sock_d = DOWEL_D + DOWEL_FIT
    m = box(-W / 2, W / 2, -D / 2, D / 2, 0, H)
    m -= cyl_x(W + 4, FEED_TROUGH_R * 2, SEG).translate((-W / 2 - 2, 0, H))
    m -= cyl_z(16.0, sock_d, SEG).translate((0, 0, -0.01))
    # pinch screw: counterbored so a stock M4 x 10 reaches the dowel
    m -= cyl_y(D, HOLE_M4_TAP).translate((0, 0, 8.0))
    m -= cyl_y(11, CB_M4).translate((0, D / 2 - 10, 8.0))
    return m

def part_feed_base():
    sock_d = DOWEL_D + DOWEL_FIT
    m = cyl_z(8.0, 70.0, SEG)                                   # flange
    m += cyl_z(28.0, 36.0, SEG)                                 # boss
    m -= cyl_z(16.5, sock_d, SEG).translate((0, 0, 12.0))       # socket
    m -= cyl_y(40, HOLE_M4_TAP).translate((0, -20, 20.0))       # pinch screw
    for i in range(3):
        a = math.radians(120 * i + 60)
        x, y = 28 * math.cos(a), 28 * math.sin(a)
        m -= cyl_z(10, HOLE_M4).translate((x, y, -1))
        m -= cyl_z(6, CB_M4).translate((x, y, 4.0))
    return m


# ──────────────────────────────────────────────────────────────────────────
# Crank: arm bolts to the drive wheel face (2 of the 4 M4 holes), free-
# spinning printed grip on an M5 bolt at the end.
# ──────────────────────────────────────────────────────────────────────────

def part_crank_arm():
    hub = cyl_z(8.0, 56.0, SEG)
    arm = box(20, 80, -10, 10, 0, 8.0)
    boss = cyl_z(8.0, 24.0, SEG_SM).translate((80, 0, 0))
    m = hub + arm + boss
    m -= cyl_z(10, 24.0, SEG_SM).translate((0, 0, -1))          # axle clearance
    # two clearance holes matching opposite pilots on the wheel's bolt circle
    for x in (-CRANK_BCD_R, CRANK_BCD_R):
        m -= cyl_z(10, HOLE_M4).translate((x, 0, -1))
    m -= cyl_z(10, HOLE_M5 - 0.2).translate((80, 0, -1))        # handle bolt
    return m

def part_crank_grip():
    m = cyl_z(32.0, 22.0, SEG)
    m -= cyl_z(34, 5.8, SEG_SM).translate((0, 0, -1))           # spins on M5
    return m


# ──────────────────────────────────────────────────────────────────────────
# Weight hanger: single plate, idler wheel bolted cantilever (M8 + nyloc),
# open hook below for the weight jar. Rides the belt's slack loop.
# ──────────────────────────────────────────────────────────────────────────

def part_weight_hanger():
    T = 10.0
    plate = box(-14, 14, 0, T, 0, 70)
    plate += cyl_y(T, 28.0, SEG_SM).translate((0, 0, 70))       # rounded top
    ring = (cyl_y(T, 30.0, SEG_SM) - cyl_y(T + 2, 15.0, SEG_SM).translate((0, -1, 0))) \
        .translate((0, 0, -8))
    gate = box(0, 20, -1, T + 1, -8, 8).rotate((0, -40, 0)).translate((0, 0, -8))
    hook = ring - gate                                          # C-hook, gate up-right
    m = plate + hook
    m -= cyl_y(T + 2, HOLE_M8).translate((0, -1, 70))           # axle hole
    return m


# ──────────────────────────────────────────────────────────────────────────
# Cord tensioner: disc drag. M5 bolt captive in the base, cord runs between
# two discs, knob (captive M5 nut) sets drag. Add a light spring or a stack
# of rubber washers between knob and outer disc for smooth adjustment.
# ──────────────────────────────────────────────────────────────────────────

def part_tensioner_base():
    m = box(0, 40, 0, 12, 0, 30)
    m -= cyl_y(14, HOLE_M5).translate((20, -1, 15))
    m -= hex_pocket_y(4.0, HEX_M5_AF).translate((20, -0.01, 15))   # captive head
    for x in (6, 34):
        m -= cyl_y(14, HOLE_M4).translate((x, -1, 15))
        m -= cyl_y(5, CB_M4).translate((x, 8.0, 15))
    return m

def part_tensioner_disc():
    m = cyl_z(4.0, 32.0, SEG)
    m -= cyl_z(6, HOLE_M5).translate((0, 0, -1))
    return m

def part_tensioner_knob():
    m = cyl_z(14.0, 26.0, SEG)
    for i in range(9):
        a = math.radians(40 * i)
        m -= cyl_z(16, 6.0, SEG_SM).translate((14.5 * math.cos(a), 14.5 * math.sin(a), -1))
    m -= cyl_z(16, HOLE_M5).translate((0, 0, -1))
    hexr = HEX_M5_AF / 2 / math.cos(math.radians(30))
    m -= Manifold.cylinder(4.5, hexr, hexr, 6).translate((0, 0, 14.0 - 4.5))
    return m


# ──────────────────────────────────────────────────────────────────────────
# Cord guide post (print 2): flat plate screwed to the board face, post
# rises past the top edge, 6 mm eye aligned with the cord run.
# ──────────────────────────────────────────────────────────────────────────

def part_cord_guide():
    T = 10.0
    plate = box(-16, 16, 0, T, 0, 30)                           # flange
    post = box(-6, 6, 0, T, 0, 66)
    post += cyl_y(T, 12.0, SEG_SM).translate((0, 0, 66))        # rounded tip
    m = plate + post
    m -= cyl_x(14, 6.0, SEG_SM).translate((-7, T / 2, 58))      # eye, along cord
    for z in (10, 22):
        m -= cyl_y(T + 2, HOLE_M4).translate((-10 if z == 10 else 10, -1, z))
        m -= cyl_y(5, CB_M4).translate((-10 if z == 10 else 10, T - 4, z))
    return m


# ──────────────────────────────────────────────────────────────────────────
# Spool bracket (print 2): open U-slot for an M8 spool axle; gravity holds
# it, draw friction gives light take-off tension.
# ──────────────────────────────────────────────────────────────────────────

def part_spool_bracket():
    T = 10.0
    m = box(0, 40, 0, T, 0, 70)
    slot = cyl_y(T + 2, 8.6).translate((20, -1, 48))
    slot += box(20 - 4.3, 20 + 4.3, -1, T + 1, 48, 71)
    m -= slot
    for z in (12, 32):
        m -= cyl_y(T + 2, HOLE_M4).translate((20, -1, z))
        m -= cyl_y(5, CB_M4).translate((20, T - 4, z))
    return m


# ──────────────────────────────────────────────────────────────────────────
# Board feet (print 2): the face board drops into the slot; screw the feet
# to the bench or a plank. One pinch screw locks the board.
# ──────────────────────────────────────────────────────────────────────────

def part_board_foot():
    m = box(0, 60, -30, 30, 0, 30)
    ch = BOARD_T + BOARD_FIT
    m -= box(-1, 61, -ch / 2, ch / 2, 8, 31)                    # board slot
    for y in (-19.6, 19.6):
        m -= cyl_z(32, HOLE_M4).translate((30, y, -1))
        m -= cyl_z(24, 9.5).translate((30, y, 8.0))             # deep cb
    # pinch screw: counterbored so a stock M4 x 10 reaches the board
    m -= cyl_y(32, HOLE_M4_TAP).translate((30, -31, 19))
    m -= cyl_y(16, CB_M4).translate((30, -31, 19))
    return m


# ──────────────────────────────────────────────────────────────────────────
# Build, validate, export
# ──────────────────────────────────────────────────────────────────────────

PARTS = {
    "drive_wheel":     (part_drive_wheel,     1),
    "idler_wheel":     (part_idler_wheel,     4),
    "bearing_spacer":  (part_bearing_spacer,  5),
    "cradle_block":    (part_cradle_block,    2),
    "feed_head":       (part_feed_head,       2),
    "feed_base":       (part_feed_base,       2),
    "crank_arm":       (part_crank_arm,       1),
    "crank_grip":      (part_crank_grip,      1),
    "weight_hanger":   (part_weight_hanger,   1),
    "tensioner_base":  (part_tensioner_base,  1),
    "tensioner_disc":  (part_tensioner_disc,  2),
    "tensioner_knob":  (part_tensioner_knob,  1),
    "cord_guide":      (part_cord_guide,      2),
    "spool_bracket":   (part_spool_bracket,   2),
    "board_foot":      (part_board_foot,      2),
}

# STLs are exported pre-rotated into print orientation: import and slice,
# no manual rotation and no supports needed.
#   cradle_block -> lies on its flat side face
#   feed_head    -> prints upright: the trough is an upward concave (fine)
#                   and the dowel socket a vertical bore whose flat ceiling
#                   bridges onto the non-critical dowel end face
#   plate parts (hanger, guides, brackets, tensioner base) -> lie flat
PRINT_ORIENT = {
    "cradle_block":   (0, 90, 0),
    "weight_hanger":  (-90, 0, 0),
    "cord_guide":     (-90, 0, 0),
    "spool_bracket":  (-90, 0, 0),
    "tensioner_base": (-90, 0, 0),
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
    tris = tm.vertices[tm.faces]
    pc = Poly3DCollection(tris, facecolor="#4a90d9", edgecolor="none", alpha=1.0)
    # simple lambert shading
    n = tm.face_normals
    light = np.array([0.4, -0.6, 0.7]); light /= np.linalg.norm(light)
    lum = np.clip(n @ light, 0, 1) * 0.7 + 0.3
    pc.set_facecolor(np.column_stack([lum * 0.29, lum * 0.56, lum * 0.85, np.ones_like(lum)]))
    ax.add_collection3d(pc)
    lo, hi = tm.bounds
    c, r = (lo + hi) / 2, (hi - lo).max() / 2 * 1.1
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_axis_off(); ax.view_init(elev=28, azim=-55)
    fig.tight_layout(pad=0)
    fig.savefig(os.path.join(PREVIEW_DIR, f"{name}.png"), dpi=110,
                bbox_inches="tight", transparent=True)
    plt.close(fig)


def main():
    print(f"{'part':<16} {'tris':>6} {'vol cm3':>8} {'genus':>5}  "
          f"{'bbox (mm)':<26} watertight")
    ok = True
    for name, (fn, qty) in PARTS.items():
        man = fn()
        if name in PRINT_ORIENT:
            man = man.rotate(PRINT_ORIENT[name])
        tm = to_trimesh(man)
        tm.apply_translation(-tm.bounds[0])          # rest on the build plate
        bb = tm.bounds
        dims = " x ".join(f"{d:.1f}" for d in (bb[1] - bb[0]))
        wt = tm.is_watertight and tm.is_winding_consistent and tm.volume > 0
        ok &= wt
        print(f"{name:<16} {len(tm.faces):>6} {tm.volume/1000:>8.1f} "
              f"{man.genus():>5}  {dims:<26} {'yes' if wt else 'NO <-- BAD'}")
        tm.export(os.path.join(HERE, f"{name}.stl"))
        render_preview(tm, name)
    print("\nAll parts watertight." if ok else "\nSOME PARTS FAILED VALIDATION")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
