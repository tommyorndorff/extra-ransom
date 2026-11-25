#!/usr/bin/env python3
"""
Parametric STL generator for the e-ink gift frame: a Waveshare 7.5" V2 raw panel
(800x480 B/W) in a slim, battery-powered landscape case with a separate desk stand.

Parts (exported in print orientation, all mm):
  front_frame  -- bezel + walls + 4 heat-set-insert bosses. Print FACE DOWN
                  (window chamfer on the bed; textured PEI gives a nice face).
  back_cover   -- screws onto the frame; carries the battery cradle, board
                  rails, FPC-adapter pad and the posts that press the panel.
                  Print OUTSIDE FACE DOWN.
  desk_stand   -- separate cradle; the case drops in and leans back STAND_TILT.
  assembly     -- preview only (not exported as STL): frame + cover + dummies.

Electronics the cavities are sized for (see the parameter block -- measure yours):
  * Waveshare 7.5" e-Paper V2 raw panel   170.2 x 111.2 x 1.18 (stated, spec)
  * DFRobot FireBeetle 2 ESP32-E           60 x 25.4 (stated), USB-C on a short end
  * Good Display DESPI-C02 FPC adapter, taped onto its pad (the Pi-HAT-sized Waveshare
    driver HAT needs ADAPTER_L ~66 and the lower posts moved -- the fit check will tell you)
  * LiPo pouch ~7 x 50 x 60 ("705060", ~2000-2500 mAh, PH2.0 lead, protected)
Hardware: 4x M3 heat-set insert (4.0 mm hole, <=6 mm long), 4x M3x8 countersunk.

Requirements:  pip install manifold3d trimesh numpy matplotlib
Usage:         python3 generate_eink_frame_stls.py
"""
import math
import os
import numpy as np
from manifold3d import Manifold, CrossSection, JoinType

HERE = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(HERE, "previews")
os.makedirs(PREVIEW_DIR, exist_ok=True)
SEG = 64

# -- panel (Waveshare 7.5" V2 spec) -----------------------------------------
PANEL_W, PANEL_H, PANEL_T = 170.2, 111.2, 1.18       # (stated)
ACTIVE_W, ACTIVE_H = 163.2, 97.92                    # (stated)
# Where the active area sits inside the outline. The 13.3 mm of vertical border
# is NOT split evenly -- the wide border is on the FPC (bottom) edge. (est.)
# Check against the mechanical drawing in the V2 spec PDF before printing.
ACTIVE_X0 = (PANEL_W - ACTIVE_W) / 2                 # 3.5 left border
ACTIVE_Y0 = 9.0                                      # bottom border (est.)
FPC_X_CENTER = PANEL_W / 2                           # FPC tail exits bottom edge (est.)
FPC_W = 16.0                                         # FPC width + slack (est.)

# -- case --------------------------------------------------------------------
PANEL_CLR = 0.3            # per side around the panel
BEZEL_SIDE = 12.0          # outer edge -> panel edge, left/right
BEZEL_TOP = 12.0
BEZEL_BOT = 22.0           # deeper "chin": hides the FPC bend, sits in the stand
WINDOW_MARGIN = 0.6        # window is this much bigger than the active area per side
WINDOW_CHAMFER = 1.0       # 45-degree chamfer on the visible window edge
FACE_T = 2.0               # front face thickness
FOAM_T = 0.5               # foam tape between face and panel glass
POCKET_DEPTH = PANEL_T + FOAM_T + 0.1
LIP_W = 1.6                # ring that locates the panel laterally
CAVITY = 9.5               # panel back -> back-cover inner face (battery 7 + tape + gap)
WALL = 2.4
CORNER_R = 6.0
BACK_T = 2.4
DEPTH = FACE_T + POCKET_DEPTH + CAVITY       # frame depth (front face -> rim)
TOTAL_T = DEPTH + BACK_T

INSERT_HOLE_D, INSERT_HOLE_DEPTH = 4.0, 6.5  # M3 heat-set (CNC-Kitchen style)
BOSS_D = 8.0
M3_CLEAR, M3_CSK_D = 3.4, 6.6

# -- electronics keep-outs (measure yours) ------------------------------------
BOARD_L, BOARD_W = 60.0, 25.4        # FireBeetle 2 ESP32-E (stated)
BOARD_CLR = 0.4
BOARD_Y_CENTER_ABOVE_BOT = 52.0      # board centre height from case bottom
USB_SLOT_W, USB_SLOT_H = 10.0, 5.0   # cutout in the right wall (long axis along Y)
USB_Z_FROM_RIM = 4.2                 # connector centre: tape 1.0 + PCB 1.6 + half of 3.2 shell
BATT_L, BATT_W = 60.0, 50.0          # LiPo footprint (+ PCM bulge on the lead end)
BATT_CLR = 1.0
ADAPTER_L, ADAPTER_W = 36.0, 32.0    # DESPI-C02 pad outline (est. -- measure yours)
RAIL_T, RAIL_H = 1.4, 3.0
POST_D = 6.0
POST_GAP = 1.0                        # gap above the panel back for a foam pad
RESET_PIN_HOLE = None                 # (x, y) in frame coords to add a 2 mm poke-hole

# -- stand --------------------------------------------------------------------
STAND_TILT = 15.0          # degrees the screen leans back from vertical
STAND_W = 120.0
STAND_D = 72.0
STAND_SLOT_CLR = 0.8       # total clearance across the case thickness
STAND_FRONT = 14.0         # stand front edge -> slot front face (at the floor)
STAND_FLOOR = 7.0          # slot floor height at its front corner
STAND_LIP_H = 17.0         # front lip top (keep below the window: BEZEL_BOT + ACTIVE_Y0)
STAND_BACK_H = 40.0

# -- derived layout (frame coordinates: X right, Y up, Z from the front face back) --
PW, PH = PANEL_W + 2 * PANEL_CLR, PANEL_H + 2 * PANEL_CLR
W = PW + 2 * BEZEL_SIDE
H = PH + BEZEL_TOP + BEZEL_BOT
PX0, PY0 = BEZEL_SIDE, BEZEL_BOT                 # panel pocket origin
PANEL_BACK_Z = FACE_T + POCKET_DEPTH
BOSS_XY = [(x, y) for x in (WALL + BOSS_D / 2 - 0.4, W - WALL - BOSS_D / 2 + 0.4)
           for y in (WALL + BOSS_D / 2 - 0.4, H - WALL - BOSS_D / 2 + 0.4)]

BOARD_BOX = (W - WALL - BOARD_L - BOARD_CLR, W - WALL,
             BOARD_Y_CENTER_ABOVE_BOT - BOARD_W / 2 - BOARD_CLR,
             BOARD_Y_CENTER_ABOVE_BOT + BOARD_W / 2 + BOARD_CLR)
BATT_BOX = (PX0 + 14, PX0 + 14 + BATT_L + 2 * BATT_CLR,
            PY0 + 42, PY0 + 42 + BATT_W + 2 * BATT_CLR)       # upper-left, clear of the adapter
ADAPTER_BOX = (PX0 + FPC_X_CENTER - ADAPTER_L / 2, PX0 + FPC_X_CENTER + ADAPTER_L / 2,
               PY0 + 6, PY0 + 6 + ADAPTER_W)
POSTS = [(PX0 + PW * fx, PY0 + 4.5) for fx in (0.12, 0.32)] + \
        [(PX0 + PW * fx, PY0 + PH - 4.5) for fx in (0.12, 0.5, 0.88)] + \
        [(PX0 + 4.5, PY0 + PH * 0.5), (PX0 + PW - 4.5, PY0 + PH * 0.82)]


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))

def cyl(x, y, z0, z1, d):
    return Manifold.cylinder(z1 - z0, d / 2, d / 2, SEG).translate((x, y, z0))

def rrect(x0, y0, w, h, r):
    cs = CrossSection.square((w - 2 * r, h - 2 * r)).translate((x0 + r, y0 + r))
    return cs.offset(r, JoinType.Round, circular_segments=SEG)

def rrect_prism(x0, y0, w, h, r, z0, z1):
    return Manifold.extrude(rrect(x0, y0, w, h, r), z1 - z0).translate((0, 0, z0))

def ring(bx, z0, z1, t):
    """Rectangular ring of wall thickness t just INSIDE box bx=(x0,x1,y0,y1)."""
    x0, x1, y0, y1 = bx
    return box(x0, x1, y0, y1, z0, z1) - box(x0 + t, x1 - t, y0 + t, y1 - t, z0 - 1, z1 + 1)

def overlaps(a, b, pad=0.0):
    return a[0] < b[1] + pad and b[0] < a[1] + pad and a[2] < b[3] + pad and b[2] < a[3] + pad


# ---------------------------------------------------------------------------

def part_front_frame():
    body = rrect_prism(0, 0, W, H, CORNER_R, 0, DEPTH)
    body -= rrect_prism(WALL, WALL, W - 2 * WALL, H - 2 * WALL, CORNER_R - WALL, FACE_T, DEPTH + 1)
    # panel locating lip (notched where the FPC folds back)
    lip = ring((PX0 - LIP_W, PX0 + PW + LIP_W, PY0 - LIP_W, PY0 + PH + LIP_W),
               FACE_T, PANEL_BACK_Z, LIP_W)
    lip -= box(PX0 + FPC_X_CENTER - FPC_W / 2, PX0 + FPC_X_CENTER + FPC_W / 2,
               PY0 - LIP_W - 1, PY0 + 1, 0, DEPTH)
    body += lip
    # window over the active area, chamfered on the visible (bed) side
    wx0 = PX0 + PANEL_CLR + ACTIVE_X0 - WINDOW_MARGIN
    wy0 = PY0 + PANEL_CLR + ACTIVE_Y0 - WINDOW_MARGIN
    ww, wh = ACTIVE_W + 2 * WINDOW_MARGIN, ACTIVE_H + 2 * WINDOW_MARGIN
    body -= box(wx0, wx0 + ww, wy0, wy0 + wh, -1, FACE_T + 1)
    c = WINDOW_CHAMFER
    # chamfer as a loft: big rectangle at z=0 shrinking to the window at z=c
    lo = CrossSection.square((ww + 2 * c, wh + 2 * c)).translate((-(ww + 2 * c) / 2, -(wh + 2 * c) / 2))
    cham = Manifold.extrude(lo, c, scale_top=(ww / (ww + 2 * c), wh / (wh + 2 * c)))
    body -= cham.translate((wx0 + ww / 2, wy0 + wh / 2, -0.001))
    # corner bosses with insert holes from the rim side
    for x, y in BOSS_XY:
        body += cyl(x, y, FACE_T - 0.01, DEPTH, BOSS_D)
        body -= cyl(x, y, DEPTH - INSERT_HOLE_DEPTH, DEPTH + 1, INSERT_HOLE_D)
    # USB-C slot through the right wall, aligned with the board's connector
    yc, zc = BOARD_Y_CENTER_ABOVE_BOT, DEPTH - USB_Z_FROM_RIM
    slot = rrect(-USB_SLOT_W / 2, -USB_SLOT_H / 2, USB_SLOT_W, USB_SLOT_H, USB_SLOT_H / 2 - 0.01)
    slot = Manifold.extrude(slot, WALL + 2)          # in (Y,Z) plane, extruded along +X
    slot = slot.transform(np.array([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]], float))
    body -= slot.translate((W - WALL - 1, yc, zc))
    return body


def back_cover_assembled():
    """Back cover in FRAME coordinates (plate at z = DEPTH .. DEPTH+BACK_T)."""
    m = rrect_prism(0, 0, W, H, CORNER_R, DEPTH, TOTAL_T)
    # locating skirt that drops just inside the walls
    sk_o, sk_t, sk_h = WALL + 0.25, 1.2, 2.0
    skirt = rrect_prism(sk_o, sk_o, W - 2 * sk_o, H - 2 * sk_o, CORNER_R - sk_o, DEPTH - sk_h, DEPTH + 0.01)
    skirt -= rrect_prism(sk_o + sk_t, sk_o + sk_t, W - 2 * (sk_o + sk_t), H - 2 * (sk_o + sk_t),
                         max(CORNER_R - sk_o - sk_t, 0.5), DEPTH - sk_h - 1, DEPTH + 1)
    for x, y in BOSS_XY:
        skirt -= cyl(x, y, DEPTH - 5, DEPTH + 1, BOSS_D + 1.6)
    yc = BOARD_Y_CENTER_ABOVE_BOT
    skirt -= box(W - WALL - 4, W, yc - BOARD_W / 2 - 2, yc + BOARD_W / 2 + 2, DEPTH - 5, DEPTH + 1)
    m += skirt
    # panel press posts (stop POST_GAP short of the panel back for a foam pad)
    for x, y in POSTS:
        m += cyl(x, y, PANEL_BACK_Z + POST_GAP, DEPTH + 0.01, POST_D)
    # board rails: both long sides + the far end, open toward the USB wall
    bx0, bx1, by0, by1 = BOARD_BOX
    z0 = DEPTH - RAIL_H
    rails = ring((bx0 - RAIL_T, bx1 + RAIL_T, by0 - RAIL_T, by1 + RAIL_T), z0, DEPTH + 0.01, RAIL_T)
    rails -= box(bx1 - 1, bx1 + RAIL_T + 1, by0 + 4, by1 - 4, z0 - 1, DEPTH + 1)   # USB end
    rails -= box(bx0 + 12, bx1 - 12, by0 - RAIL_T - 1, by1 + RAIL_T + 1, z0 - 1, DEPTH + 1)  # pin access
    rails -= box(W - WALL - 0.3, W + 1, 0, H, z0 - 1, DEPTH + 1)      # stay clear of the wall
    m += rails
    # battery corner cradle (L-shaped corners, leads exit anywhere)
    ax0, ax1, ay0, ay1 = BATT_BOX
    cr = ring((ax0 - RAIL_T, ax1 + RAIL_T, ay0 - RAIL_T, ay1 + RAIL_T), DEPTH - 4, DEPTH + 0.01, RAIL_T)
    cr -= box(ax0 + 10, ax1 - 10, ay0 - 5, ay1 + 5, 0, TOTAL_T + 1)
    cr -= box(ax0 - 5, ax1 + 5, ay0 + 10, ay1 - 10, 0, TOTAL_T + 1)
    m += cr
    # FPC adapter locating pad (low ridge)
    m += ring(ADAPTER_BOX, DEPTH - 1.0, DEPTH + 0.01, 0.8)
    # screw holes, countersunk on the outside face
    for x, y in BOSS_XY:
        m -= cyl(x, y, DEPTH - 1, TOTAL_T + 1, M3_CLEAR)
        csk_h = (M3_CSK_D - M3_CLEAR) / 2
        m -= Manifold.cylinder(csk_h + 0.01, M3_CLEAR / 2, M3_CSK_D / 2 + 0.01, SEG).translate(
            (x, y, TOTAL_T - csk_h))
    if RESET_PIN_HOLE:
        m -= cyl(*RESET_PIN_HOLE, DEPTH - 5, TOTAL_T + 1, 2.0)
    return m


def part_back_cover():
    # flip so the outside face is on the bed (z = 0)
    return back_cover_assembled().mirror((0, 0, 1)).translate((0, 0, TOTAL_T))


def part_desk_stand():
    t = math.radians(STAND_TILT)
    T = TOTAL_T + STAND_SLOT_CLR
    up, nrm = np.array([math.sin(t), math.cos(t)]), np.array([math.cos(t), -math.sin(t)])
    p0 = np.array([STAND_FRONT, STAND_FLOOR])
    p1 = p0 + T * nrm
    L = 120
    slot = [p0, p1, p1 + L * up, p0 + L * up]
    # back face of the case at STAND_BACK_H, plus a 7 mm shoulder behind it
    back_y = p1[0] + (STAND_BACK_H - p1[1]) * math.tan(t)
    prof = [(0, 0), (STAND_D, 0), (STAND_D, 8), (back_y + 7, STAND_BACK_H), (back_y - 1, STAND_BACK_H),
            (STAND_FRONT - 3, STAND_LIP_H), (2.5, STAND_LIP_H), (0, STAND_LIP_H - 2.5)]
    perm = np.array([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]], float)   # (u,v,extrude) -> (Y,Z,X)
    body = Manifold.extrude(CrossSection([np.array(prof, float)]), STAND_W).transform(perm)
    cut = Manifold.extrude(CrossSection([np.array(slot, float)]), STAND_W + 2).transform(perm)
    body -= cut.translate((-1, 0, 0))
    # felt-pad recesses on the underside (10 mm dots, 1 mm deep)
    for x in (10, STAND_W - 10):
        for y in (10, STAND_D - 10):
            body -= cyl(x, y, -1, 1.0, 10.5)
    return body


def dummies():
    """Panel, board, battery and adapter as solids, for the fit check + preview."""
    ox, oy = PX0 + PANEL_CLR, PY0 + PANEL_CLR
    panel = box(ox, ox + PANEL_W, oy, oy + PANEL_H, FACE_T + FOAM_T, FACE_T + FOAM_T + PANEL_T)
    bx0, bx1, by0, by1 = BOARD_BOX
    board = box(bx0 + BOARD_CLR, bx1, by0 + BOARD_CLR, by1 - BOARD_CLR, DEPTH - 6.0, DEPTH - 1.0)
    ax0, ax1, ay0, ay1 = BATT_BOX
    batt = box(ax0 + BATT_CLR, ax1 - BATT_CLR, ay0 + BATT_CLR, ay1 - BATT_CLR, DEPTH - 7.5, DEPTH - 0.5)
    a = ADAPTER_BOX
    adapter = box(a[0] + 1, a[1] - 1, a[2] + 1, a[3] - 1, DEPTH - 4.5, DEPTH - 1.0)
    return {"panel": panel, "board": board, "battery": batt, "adapter": adapter}


def fit_check():
    problems = []
    keepouts = {"board": BOARD_BOX, "battery": BATT_BOX, "adapter": ADAPTER_BOX}
    names = list(keepouts)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if overlaps(keepouts[a], keepouts[b], pad=RAIL_T):
                problems.append(f"{a} overlaps {b}")
    for x, y in POSTS:
        pb = (x - POST_D / 2, x + POST_D / 2, y - POST_D / 2, y + POST_D / 2)
        for n, k in keepouts.items():
            if overlaps(pb, k, pad=RAIL_T):
                problems.append(f"post at ({x:.0f},{y:.0f}) hits {n}")
    frame, cover = part_front_frame(), back_cover_assembled()
    v = (frame ^ cover).volume()
    if v > 1.0:
        problems.append(f"frame/back-cover interference {v:.1f} mm3")
    for n, d in dummies().items():
        for pn, p in (("frame", frame), ("back cover", cover)):
            v = (d ^ p).volume()
            if v > 1.0:
                problems.append(f"{n} intersects {pn} ({v:.1f} mm3)")
    if STAND_LIP_H >= BEZEL_BOT + ACTIVE_Y0:
        problems.append("stand lip would cover the bottom of the screen")
    return problems


PARTS = {
    "front_frame": part_front_frame,
    "back_cover": part_back_cover,
    "desk_stand": part_desk_stand,
}


def to_trimesh(man):
    import trimesh
    mesh = man.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties, dtype=np.float64)[:, :3],
                           faces=np.asarray(mesh.tri_verts, dtype=np.int64), process=True)


def render_preview(parts, name, elev=28, azim=-55):
    """parts: list of (trimesh, rgb)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(projection="3d")
    light = np.array([0.4, -0.6, 0.7]); light /= np.linalg.norm(light)
    lo_all, hi_all = [], []
    for tm, rgb in parts:
        pc = Poly3DCollection(tm.vertices[tm.faces], edgecolor="none")
        lum = np.clip(tm.face_normals @ light, 0, 1) * 0.7 + 0.3
        pc.set_facecolor(np.column_stack([lum * rgb[0], lum * rgb[1], lum * rgb[2], np.ones_like(lum)]))
        ax.add_collection3d(pc)
        lo_all.append(tm.bounds[0]); hi_all.append(tm.bounds[1])
    lo, hi = np.min(lo_all, axis=0), np.max(hi_all, axis=0)
    c, r = (lo + hi) / 2, (hi - lo).max() / 2 * 1.05
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_axis_off(); ax.view_init(elev=elev, azim=azim)
    fig.tight_layout(pad=0)
    fig.savefig(os.path.join(PREVIEW_DIR, f"{name}.png"), dpi=110, bbox_inches="tight", transparent=True)
    plt.close(fig)


def main():
    print(f"case {W:.1f} x {H:.1f} x {TOTAL_T:.1f} mm  "
          f"({W / 25.4:.2f} x {H / 25.4:.2f} x {TOTAL_T / 25.4:.2f} in)")
    print(f"{'part':<12} {'tris':>6} {'vol cm3':>8} {'genus':>5}  {'bbox (mm)':<26} watertight")
    ok = True
    for name, fn in PARTS.items():
        man = fn()
        tm = to_trimesh(man)
        tm.apply_translation(-tm.bounds[0])
        dims = " x ".join(f"{d:.1f}" for d in (tm.bounds[1] - tm.bounds[0]))
        wt = tm.is_watertight and tm.is_winding_consistent and tm.volume > 0
        ok &= wt
        print(f"{name:<12} {len(tm.faces):>6} {tm.volume / 1000:>8.1f} {man.genus():>5}  "
              f"{dims:<26} {'yes' if wt else 'NO <-- BAD'}")
        tm.export(os.path.join(HERE, f"{name}.stl"))
        render_preview([(tm, (0.55, 0.42, 0.28))], name)
    # exploded assembly preview: back cover lifted 25 mm, dummies coloured
    d = dummies()
    asm = [(to_trimesh(part_front_frame()), (0.55, 0.42, 0.28)),
           (to_trimesh(back_cover_assembled().translate((0, 0, 25))), (0.45, 0.45, 0.5)),
           (to_trimesh(d["panel"]), (0.85, 0.85, 0.8)),
           (to_trimesh(d["board"].translate((0, 0, 25))), (0.2, 0.4, 0.8)),
           (to_trimesh(d["battery"].translate((0, 0, 25))), (0.8, 0.6, 0.1)),
           (to_trimesh(d["adapter"].translate((0, 0, 25))), (0.2, 0.6, 0.3))]
    render_preview(asm, "assembly_exploded", elev=-35, azim=-60)
    problems = fit_check()
    for p in problems:
        print("FIT:", p)
    ok &= not problems
    print("\nAll parts watertight, fit check clean." if ok else "\nSOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
