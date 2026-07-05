#!/usr/bin/env python3
"""
Parametric STL generator for the Ring-Flyer Orbit Binder - a hypothetical
rod binder that inverts the Garrison principle: the rod stays stationary
and the binding-cord spool orbits around it on a gear-driven ring, like a
cable-serving machine. See the project page for the full design rationale.

Requirements:  pip install manifold3d trimesh numpy matplotlib
Usage:         python3 generate_ring_flyer_stls.py
Output:        ./<part>.stl + ./previews/<part>.png next to this script.
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

# ──────────────────────────────────────────────────────────────────────────
# PARAMETERS
# ──────────────────────────────────────────────────────────────────────────

# Gearing: module 2, 20 deg pressure angle, 3:1 ratio
MODULE = 2.0
RING_TEETH = 78          # ring gear PD 156
PINION_TEETH = 26        # pinion PD 52; centre distance 104
PRESSURE_ANGLE = 20.0
BACKLASH = 0.25          # total circumferential backlash for FDM gears

RING_BORE_D = 90.0       # rod sections thread through this
RING_LEN = 30.0          # total axial length
GEAR_ZONE = 10.0         # rear 10 mm carries the gear teeth
RACE_BASE_D = 134.0      # V-ridge base diameter
RACE_CREST_D = 146.0     # V-ridge crest diameter (90 deg included ridge)
FURN_BCD = 110.0         # bolt circle for ring-face furniture (M4)
FURN_SPACING = 42.1      # chord between adjacent BCD holes (45 deg apart)

# 608 bearings, same tuning rule as the Garrison build
POCKET_D = 22.15
POCKET_DEPTH = 7.1

ROLLER_OD = 34.0
ROLLER_W = 18.0
ROLLER_ROOT_D = 26.0     # 90 deg included V-groove root
ROLLER_R_POS = 86.5      # roller axle radius from ring centre

HOLE_M8 = 8.4
HOLE_M5 = 5.5
HOLE_M4 = 4.5
HOLE_M4_TAP = 3.6
CB_M4 = 8.8
HEX_M4_AF = 7.3          # captive pocket for M4 nut (7.0 nominal)
HEX_M5_AF = 8.3
HEX_M8_AF = 13.4         # captive pocket for M8 nut (13.0 nominal)

PLATE_T = 12.0
RING_STANDOFF = 6.0      # ring rear face to plate front face
RACE_PLANE_Z = 20.0      # race centre, measured from the ring's rear face
# roller groove centre must land in the race plane:
STANDOFF_LEN = RING_STANDOFF + RACE_PLANE_Z - ROLLER_W / 2   # 17.0

# ──────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────

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


def involute_gear_profile(z, m, pa_deg=20.0, backlash=0.25, pts=10):
    """2D involute spur gear outline (external), tooth-thinned for FDM.

    Returns a list of (x, y) tracing the full gear silhouette CCW.
    """
    pa = math.radians(pa_deg)
    rp = m * z / 2                 # pitch radius
    rb = rp * math.cos(pa)         # base radius
    ra = rp + m                    # addendum radius
    rf = rp - 1.25 * m             # dedendum radius

    def inv(a):                    # involute function
        return math.tan(a) - a

    # half tooth angular thickness at pitch circle; each mating gear is
    # thinned by backlash/2, giving `backlash` total in the mesh
    half_t = math.pi / (2 * z) + inv(pa) - backlash / (4 * rp)

    prof = []
    for i in range(z):
        pitch_c = 2 * math.pi * i / z          # tooth centreline angle
        # involute flank samples from max(rf, rb) out to ra
        r0 = max(rf, rb)
        flank = []
        for j in range(pts + 1):
            r = r0 + (ra - r0) * j / pts
            t = math.sqrt(max((r / rb) ** 2 - 1, 0.0))   # involute parameter
            ang = t - math.atan(t)                       # involute polar angle
            flank.append((r, ang))
        # CCW traversal: right flank root->tip, left flank tip->root,
        # then the tooth gap traced as an ARC on the root circle (a chord
        # here would bulge into the mating tooth's tip sweep and bind).
        for r, ang in flank:
            a = pitch_c - half_t + ang
            prof.append((r * math.cos(a), r * math.sin(a)))
        for r, ang in reversed(flank):
            a = pitch_c + half_t - ang
            prof.append((r * math.cos(a), r * math.sin(a)))
        a1 = pitch_c + half_t - flank[0][1]              # gap start
        a2 = pitch_c + 2 * math.pi / z - half_t + flank[0][1]   # gap end
        for j in range(1, 6):
            a = a1 + (a2 - a1) * j / 6
            prof.append((rf * math.cos(a), rf * math.sin(a)))
    return prof


def gear_solid(z, m, width, backlash=BACKLASH):
    prof = involute_gear_profile(z, m, PRESSURE_ANGLE, backlash)
    return CrossSection([prof]).extrude(width)


# ──────────────────────────────────────────────────────────────────────────
# Orbit ring: bore 90, rear 10 mm gear (z=78), front V-ridge race,
# rear lightening pocket, 8 captive-M4-nut furniture points on the front.
# ──────────────────────────────────────────────────────────────────────────

def part_orbit_ring():
    m = gear_solid(RING_TEETH, MODULE, GEAR_ZONE)                # rear gear
    m += cyl_z(RING_LEN, RACE_BASE_D, SEG)                       # body
    # V-ridge race: revolved triangle, crest at z = 20 (race centre)
    rb, rc = RACE_BASE_D / 2, RACE_CREST_D / 2
    ridge_h = rc - rb                                            # 6 mm
    prof = CrossSection([[
        (rb - 0.1, 20 - ridge_h),
        (rc, 20.0),
        (rb - 0.1, 20 + ridge_h),
    ]])
    m += prof.revolve(SEG)
    # bore
    m -= cyl_z(RING_LEN + 2, RING_BORE_D, SEG).translate((0, 0, -1))
    # furniture: 8x M4 holes, each fed by a hex shaft from the rear face.
    # Lay the ring front-face-down, drop an M4 nut down each shaft: it
    # lands on the web shoulder, held anti-rotation by the hex, and the
    # bolt threads in from the front. Shaft crowns are ~7 mm bridges.
    for i in range(8):
        a = math.radians(45 * i)
        x, y = FURN_BCD / 2 * math.cos(a), FURN_BCD / 2 * math.sin(a)
        m -= cyl_z(10, HOLE_M4).translate((x, y, RING_LEN - 9))
        m -= hexagon_z(22.0, HEX_M4_AF).rotate((0, 0, 45 * i)) \
            .translate((x, y, -0.01))
    # round lightening bores between the furniture stations
    for i in range(8):
        a = math.radians(45 * i + 22.5)
        x, y = FURN_BCD / 2 * math.cos(a), FURN_BCD / 2 * math.sin(a)
        m -= cyl_z(22.0, 16.0, SEG_SM).translate((x, y, -0.01))
    return m


# ──────────────────────────────────────────────────────────────────────────
# Stanchion plate: carries 4 V-rollers, the pinion, and two feet.
# Local origin = ring centre; plate spans x -68..140, y -135..77.
# ──────────────────────────────────────────────────────────────────────────

def part_stanchion_plate():
    m = box(-68, 140, -135, 77, 0, PLATE_T)
    m -= cyl_z(PLATE_T + 2, 100.0, SEG).translate((0, 0, -1))    # rod window
    # roller axles at r 86.5; the two TOP axles (45 and 135 deg) sit in
    # radial slots so preload closes both diagonals onto the fixed pair
    for ang in (225, 315):
        a = math.radians(ang)
        x, y = ROLLER_R_POS * math.cos(a), ROLLER_R_POS * math.sin(a)
        m -= cyl_z(PLATE_T + 2, HOLE_M8 + 0.1).translate((x, y, -1))
    # slot travel: +2.75 outward (assembly ease), only +0.75 inward so a
    # fully-preloaded roller's standoff still clears the gear tips (r80)
    for ang in (45, 135):
        a = math.radians(ang)
        for rr in (ROLLER_R_POS - 0.75, ROLLER_R_POS + 2.75):
            m -= cyl_z(PLATE_T + 2, HOLE_M8 + 0.1) \
                .translate((rr * math.cos(a), rr * math.sin(a), -1))
        sl = box(-1.75, 1.75, -(HOLE_M8 + 0.1) / 2, (HOLE_M8 + 0.1) / 2,
                 -1, PLATE_T + 1) \
            .rotate((0, 0, ang)).translate(((ROLLER_R_POS + 1) * math.cos(a),
                                            (ROLLER_R_POS + 1) * math.sin(a), 0))
        m -= sl
    # pinion axle
    m -= cyl_z(PLATE_T + 2, HOLE_M8 + 0.1).translate((104, 0, -1))
    # feet: walls rising from the plate in print orientation; in use the
    # plate stands vertical and these lie on the board
    for fx in (-64, 60):
        foot = box(fx, fx + 60, -135, -125, PLATE_T, PLATE_T + 28)
        for hx in (fx + 15, fx + 45):
            foot -= cyl_y(12, HOLE_M4).translate((hx, -136, PLATE_T + 14))
            foot -= cyl_y(6, CB_M4).translate((hx, -131, PLATE_T + 14))
        m += foot
    return m


# ──────────────────────────────────────────────────────────────────────────
# V-roller (print 4): rides the ring's V-ridge; V-in-V locates the ring
# radially and axially. Two 608s per roller.
# ──────────────────────────────────────────────────────────────────────────

def part_v_roller():
    r = ROLLER_OD / 2
    m = Manifold.cylinder(ROLLER_W, r, r, SEG)
    root_r = ROLLER_ROOT_D / 2
    depth = r - root_r
    over = 2.0
    hw_rim = (depth + over)                     # 45 deg walls, no root flat
    prof = CrossSection([[
        (root_r, ROLLER_W / 2),
        (r + over, ROLLER_W / 2 - hw_rim),
        (r + over, ROLLER_W / 2 + hw_rim),
    ]])
    m -= prof.revolve(SEG)
    pr = POCKET_D / 2
    m -= cyl_z(POCKET_DEPTH, POCKET_D, SEG).translate((0, 0, -0.01))
    m -= Manifold.cylinder(0.8, pr + 0.8, pr, SEG)
    m -= cyl_z(POCKET_DEPTH + 0.01, POCKET_D, SEG) \
        .translate((0, 0, ROLLER_W - POCKET_DEPTH))
    m -= Manifold.cylinder(0.8, pr, pr + 0.8, SEG) \
        .translate((0, 0, ROLLER_W - 0.8))
    m -= cyl_z(ROLLER_W + 2, 19.0, SEG).translate((0, 0, -1))
    return m


def part_roller_spacer():
    """Between the two 608 inner races inside each roller."""
    web = ROLLER_W - 2 * POCKET_DEPTH
    return cyl_z(web + 0.3, 12.0, SEG_SM) \
        - cyl_z(web + 2.3, 8.4, SEG_SM).translate((0, 0, -1))


def part_roller_standoff():
    """Plate-to-roller spacer tube: puts the roller groove centre in the
    ring's race plane (17 mm off the plate). OD 11 so the tube clears the
    orbiting ring's gear tips (r80) with 1.0 mm margin: 86.5 - 5.5 = 81."""
    return cyl_z(STANDOFF_LEN, 11.0, SEG_SM) \
        - cyl_z(STANDOFF_LEN + 2, HOLE_M8, SEG_SM).translate((0, 0, -1))


def part_pinion_shim():
    """Plate-to-pinion washer: lifts the pinion 3.25 mm so its 14 mm gear
    face fully covers the ring's 10 mm gear band, with running clearance
    to the plate."""
    return cyl_z(3.25, 12.0, SEG_SM) \
        - cyl_z(5.25, 8.4, SEG_SM).translate((0, 0, -1))


# ──────────────────────────────────────────────────────────────────────────
# Pinion + crank hub: one body. Rear 14 mm is the z=26 gear; a long hub
# carries the crank plane 60 mm clear of the ring furniture. 608s at both
# extreme ends of the through-bore.
# ──────────────────────────────────────────────────────────────────────────

PINION_LEN = 93.0

def part_pinion_crank():
    m = gear_solid(PINION_TEETH, MODULE, 14.0)
    m += cyl_z(PINION_LEN - 10, 26.0, SEG)
    # 45-deg cone up to the crank flange, then the flange
    m += Manifold.cylinder(7.0, 13.0, 20.0, SEG).translate((0, 0, PINION_LEN - 17))
    m += cyl_z(10.0, 40.0, SEG).translate((0, 0, PINION_LEN - 10))
    # bore + bearing pockets at both ends
    m -= cyl_z(PINION_LEN + 2, 12.0, SEG).translate((0, 0, -1))
    pr = POCKET_D / 2
    m -= cyl_z(POCKET_DEPTH, POCKET_D, SEG).translate((0, 0, -0.01))
    m -= Manifold.cylinder(0.8, pr + 0.8, pr, SEG)
    m -= cyl_z(POCKET_DEPTH + 0.01, POCKET_D, SEG) \
        .translate((0, 0, PINION_LEN - POCKET_DEPTH))
    m -= Manifold.cylinder(0.8, pr, pr + 0.8, SEG) \
        .translate((0, 0, PINION_LEN - 0.8))
    # crank-arm self-tap pilots in the flange face (14 deep: flange + cone)
    for x in (-14, 14):
        m -= cyl_z(14, HOLE_M4_TAP).translate((x, 0, PINION_LEN - 14))
    return m


def part_pinion_spacer():
    return cyl_z(PINION_LEN - 2 * POCKET_DEPTH + 0.3, 12.0, SEG_SM) \
        - cyl_z(PINION_LEN, 8.4, SEG_SM).translate((0, 0, -1))


def part_crank_arm():
    # 35 mm centres: swing inner radius 104 - 35 - 11 = 58 mm from the
    # ring axis, clearing the O90 bore (r45) and the rod by 13 mm
    m = cyl_z(8.0, 44.0, SEG)
    m += box(0, 35, -7.5, 7.5, 0, 8.0)
    m += cyl_z(8.0, 22.0, SEG_SM).translate((35, 0, 0))
    m -= cyl_z(10, 19.0, SEG_SM).translate((0, 0, -1))   # clears axle nyloc
    for x in (-14, 14):
        m -= cyl_z(10, HOLE_M4).translate((x, 0, -1))
    m -= cyl_z(10, HOLE_M5 - 0.2).translate((35, 0, -1))
    return m


def part_knob_post():
    """Primary drive: a spinner-knob post bolted to the ring face. The
    sleeve (knob_sleeve) free-spins on the integral post; you whirl the
    ring directly, 1 rev = 1 wrap. The geared pinion crank remains as the
    slow 3:1 fine drive for delicate tip work."""
    m = furniture_base(20.0)
    m += cyl_z(45.0, 9.0, SEG_SM).translate((0, 0, 8))
    m -= cyl_z(9, HOLE_M4_TAP).translate((0, 0, 53 - 8))   # retaining screw
    return m


def part_knob_sleeve():
    return cyl_z(40.0, 22.0, SEG) \
        - cyl_z(42, 9.6, SEG_SM).translate((0, 0, -1))


def part_crank_grip():
    return cyl_z(40.0, 22.0, SEG) \
        - cyl_z(42, 5.8, SEG_SM).translate((0, 0, -1))


# ──────────────────────────────────────────────────────────────────────────
# Ring furniture: every base is 50 mm long with two counterbored M4 holes
# 42.1 mm apart (adjacent holes of the ring's bolt circle).
# ──────────────────────────────────────────────────────────────────────────

def furniture_base(width=20.0, thick=8.0):
    m = box(-25, 25, -width / 2, width / 2, 0, thick)
    for x in (-FURN_SPACING / 2, FURN_SPACING / 2):
        m -= cyl_z(thick + 2, HOLE_M4).translate((x, 0, -1))
        m -= cyl_z(thick, CB_M4).translate((x, 0, 3.5))
    return m


def part_spool_post():
    m = furniture_base(25.0)
    boss = cyl_z(12.0, 18.0, SEG_SM)
    m += boss.rotate((-90, 0, 0)).translate((0, -6, 22))          # axis normal-ish
    m += box(-9, 9, -12.5, 6, 8, 27)                              # riser (full head seat)
    hole = cyl_y(40, HOLE_M8).translate((0, -21, 22))
    m -= hole
    return m


def part_spool():
    m = cyl_z(3.0, 50.0, SEG)                                     # flange
    m += cyl_z(33.0, 20.0, SEG)                                   # core
    # 45-deg cone under the top flange so it prints support-free
    m += Manifold.cylinder(15.0, 10.0, 25.0, SEG).translate((0, 0, 18))
    m += cyl_z(3.0, 50.0, SEG).translate((0, 0, 33))              # flange
    m -= cyl_z(40, HOLE_M8, SEG_SM).translate((0, 0, -1))
    return m


def part_tensioner_base():
    m = furniture_base(25.0)
    m += cyl_z(4.0, 16.0, SEG_SM).translate((0, 0, 8))            # boss
    m -= cyl_z(14, HOLE_M5).translate((0, 0, -1))
    m -= hexagon_z(4.0, HEX_M5_AF).translate((0, 0, -0.01))       # captive head
    return m


def part_tensioner_disc():
    return cyl_z(4.0, 30.0, SEG) - cyl_z(6, HOLE_M5).translate((0, 0, -1))


def part_tensioner_knob():
    m = cyl_z(14.0, 26.0, SEG)
    for i in range(9):
        a = math.radians(40 * i)
        m -= cyl_z(16, 6.0, SEG_SM) \
            .translate((14.5 * math.cos(a), 14.5 * math.sin(a), -1))
    m -= cyl_z(16, HOLE_M5).translate((0, 0, -1))
    m -= hexagon_z(4.5, HEX_M5_AF).translate((0, 0, 14.0 - 4.5))
    return m


def part_guide_pin():
    m = furniture_base()
    m += cyl_z(14.0, 8.0, SEG_SM).translate((0, 0, 8))            # pin
    m += Manifold.cylinder(3.0, 4.0, 7.0, SEG_SM).translate((0, 0, 8))
    # upward 45-deg flare supports the retaining flange (support-free)
    m += Manifold.cylinder(3.0, 4.0, 7.0, SEG_SM).translate((0, 0, 19))
    m += cyl_z(2.0, 14.0, SEG_SM).translate((0, 0, 22))           # top flange
    return m


def part_fairlead():
    m = furniture_base()
    m += box(-8.5, 8.5, -5, 5, 8, 30)                             # post (wide:
    # covers the eye boss underside past the 50-deg overhang tangent)
    eye = cyl_z(8.0, 26.0, SEG_SM).rotate((0, 90, 0)).translate((-4, 0, 30))
    m += eye
    m -= cyl_x(10, 8.0, SEG_SM).translate((-5, 0, 30))            # eye hole
    # chamfered eye edges (cone reliefs both sides)
    m -= Manifold.cylinder(2.0, 6.0, 4.0, SEG_SM).rotate((0, 90, 0)) \
        .translate((-4.01, 0, 30))
    m -= Manifold.cylinder(2.0, 4.0, 6.0, SEG_SM).rotate((0, 90, 0)) \
        .translate((2.01, 0, 30))
    return m


def part_counterweight_cup():
    m = furniture_base(30.0)
    m += box(-22.5, 22.5, -15, 15, 8, 30)
    m -= box(-20.5, 20.5, -13, 13, 10, 31)                        # cavity
    return m


# ──────────────────────────────────────────────────────────────────────────
# Rod supports: V-head threads onto an M8 rod column into a base; height
# set by threading, locked with jam nuts.
# ──────────────────────────────────────────────────────────────────────────

def part_support_head():
    m = box(-20, 20, -15, 15, 0, 28)
    # 90-deg V-groove, 15 deep, along X
    vg = CrossSection([[(-16, 1), (0, -15), (16, 1)]]) \
        .extrude(44).rotate((90, 0, 0)).rotate((0, 0, 90))
    m -= vg.translate((-22, 0, 28))
    m -= cyl_z(12, HOLE_M8 + 0.2).translate((0, 0, -1))
    m -= hexagon_z(7.0, HEX_M8_AF).translate((0, 0, -0.01))
    return m


def part_support_base():
    m = cyl_z(15.0, 60.0, SEG)
    m -= cyl_z(17, HOLE_M8 + 0.2).translate((0, 0, -1))
    m -= hexagon_z(7.0, HEX_M8_AF).translate((0, 0, 15.0 - 7.0))
    for i in range(3):
        a = math.radians(120 * i + 60)
        x, y = 22.5 * math.cos(a), 22.5 * math.sin(a)
        m -= cyl_z(18, HOLE_M4).translate((x, y, -1))
        m -= cyl_z(8, CB_M4).translate((x, y, 8.0))
    return m


def part_centering_gauge():
    # steps sized for HEX sections: bore = 1.16 x across-flats + clearance
    # for AF 10 / 8 / 6 / 4 / 2 mm strips
    m = cyl_z(10.0, 89.6, SEG)
    z = 10.0
    for d in (11.9, 9.6, 7.2, 4.9, 2.6):
        z -= 2.0
        m -= cyl_z(12, d, SEG_SM).translate((0, 0, z))
    return m


# ──────────────────────────────────────────────────────────────────────────
# Build, validate, export
# ──────────────────────────────────────────────────────────────────────────

PARTS = {
    "orbit_ring":       (part_orbit_ring,       1),
    "stanchion_plate":  (part_stanchion_plate,  1),
    "v_roller":         (part_v_roller,         4),
    "roller_spacer":    (part_roller_spacer,    4),
    "roller_standoff":  (part_roller_standoff,  4),
    "pinion_crank":     (part_pinion_crank,     1),
    "pinion_spacer":    (part_pinion_spacer,    1),
    "pinion_shim":      (part_pinion_shim,      1),
    "crank_arm":        (part_crank_arm,        1),
    "crank_grip":       (part_crank_grip,       1),
    "knob_post":        (part_knob_post,        1),
    "knob_sleeve":      (part_knob_sleeve,      1),
    "spool_post":       (part_spool_post,       1),
    "spool":            (part_spool,            1),
    "tensioner_base":   (part_tensioner_base,   1),
    "tensioner_disc":   (part_tensioner_disc,   2),
    "tensioner_knob":   (part_tensioner_knob,   1),
    "guide_pin":        (part_guide_pin,        1),
    "fairlead":         (part_fairlead,         1),
    "counterweight_cup": (part_counterweight_cup, 1),
    "support_head":     (part_support_head,     2),
    "support_base":     (part_support_base,     2),
    "centering_gauge":  (part_centering_gauge,  1),
}

PRINT_ORIENT = {}      # everything already exports in print orientation


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
    pc = Poly3DCollection(tris, edgecolor="none")
    n = tm.face_normals
    light = np.array([0.4, -0.6, 0.7]); light /= np.linalg.norm(light)
    lum = np.clip(n @ light, 0, 1) * 0.7 + 0.3
    pc.set_facecolor(np.column_stack(
        [lum * 0.85, lum * 0.45, lum * 0.25, np.ones_like(lum)]))
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
    print(f"{'part':<18} {'tris':>6} {'vol cm3':>8} {'genus':>5}  "
          f"{'bbox (mm)':<28} watertight")
    ok = True
    for name, (fn, qty) in PARTS.items():
        man = fn()
        if name in PRINT_ORIENT:
            man = man.rotate(PRINT_ORIENT[name])
        tm = to_trimesh(man)
        tm.apply_translation(-tm.bounds[0])
        bb = tm.bounds
        dims = " x ".join(f"{d:.1f}" for d in (bb[1] - bb[0]))
        wt = tm.is_watertight and tm.is_winding_consistent and tm.volume > 0
        ok &= wt
        print(f"{name:<18} {len(tm.faces):>6} {tm.volume/1000:>8.1f} "
              f"{man.genus():>5}  {dims:<28} {'yes' if wt else 'NO <-- BAD'}")
        tm.export(os.path.join(HERE, f"{name}.stl"))
        render_preview(tm, name)
    print("\nAll parts watertight." if ok else "\nSOME PARTS FAILED VALIDATION")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
