#!/usr/bin/env python3
"""
Parametric barn / schoolhouse lamp shade for a UNO-fitter socket.
Generates print-ready STLs sized for a Bambu P1S (256 x 256 mm bed).

Only needs numpy:  python3 make_shade.py
All dimensions in mm. Profile is in (r, z) with z = 0 at the rim (print rim-down).
"""
import numpy as np, struct, os, json

# ------------------------------------------------------------------ parameters
P = dict(
    style        = "barn",   # "barn" (image 1) or "cone" (image 2 schoolhouse style)
    diameter     = 305.0,    # rim outer diameter (12" = 304.8)
    wall         = 2.4,      # shell thickness (also top clamp plate thickness)
    hole_d       = 44.8,     # UNO opening (1.75" = 44.45; +0.35 clearance) - measure yours!
    # fitter cap: must clear the UNO ring inside it
    cap_d        = 78.0,     # outer dia of top tier at the plate
    cap_h        = 24.0,
    tier_d       = 116.0,    # outer dia of lower tier (barn only)
    tier_h       = 20.0,
    # splitting
    one_piece_max= 250.0,    # print whole if rim dia <= this (P1S bed is 256)
    max_piece    = 238.0,    # widest hub piece when split
    ring_pieces  = 4,        # rim ring segments when the shade is split
    joint_len    = 9.0,      # how far the hub's internal sleeve reaches below the seam
    joint_t      = 2.0,      # sleeve / splice plate thickness
    gap          = 0.2,      # slip clearance on mating surfaces
    splice_deg   = 20.0,     # angular width of each radial-seam splice plate
    seg_deg      = 1.0,      # angular resolution
    out          = "out",
)

# ------------------------------------------------------------------ profile
def bezier(p0, p1, p2, p3, n=90):
    t = np.linspace(0, 1, n)[:, None]
    return ((1-t)**3)*p0 + 3*((1-t)**2)*t*p1 + 3*(1-t)*t*t*p2 + t**3*p3

def outer_profile(p):
    R = p["diameter"] / 2
    s = R / 152.5                      # dome scales with size; fitter cap does not
    rh, rc, rt = p["hole_d"]/2, p["cap_d"]/2, p["tier_d"]/2
    pts = [(R, 0.0), (R - 0.8, 7.0*s)]          # short rim skirt
    if p["style"] == "barn":
        z_d = 7.0*s + 80.0*s
        dome = bezier(np.array(pts[-1]), np.array([R - 3*s, 7*s + 44*s]),
                      np.array([0.70*R, z_d - 7*s]), np.array([rt + 5.0, z_d]))
        pts += [tuple(q) for q in dome[1:]]
        z = z_d
        pts += [(rt, z), (rt - 3.0, z + p["tier_h"])]          # lower tier
        z += p["tier_h"]
        pts += [(rc + 3.0, z), (rc, z + p["cap_h"])]           # upper tier / fitter cap
        z += p["cap_h"]
    else:  # cone / schoolhouse
        slope = np.radians(17)
        r_top = rc + 8.0
        z_c = pts[-1][1] + (pts[-1][0] - r_top) * np.tan(slope)
        cone = bezier(np.array(pts[-1]), np.array([R - 12, pts[-1][1] + 4]),
                      np.array([r_top + 20, z_c - 2]), np.array([r_top, z_c]), 40)
        pts += [tuple(q) for q in cone[1:]]
        z = z_c
        pts += [(rc, z + 2), (rc, z + p["cap_h"])]
        z += p["cap_h"]
    pts += [(rh, z)]                                            # clamp plate -> hole
    return np.array(pts)

def offset(curve, d):
    """Offset an open polyline toward the shade interior by d (mitred corners)."""
    seg = np.diff(curve, axis=0)
    seg /= np.linalg.norm(seg, axis=1)[:, None]
    nrm = np.stack([-seg[:, 1], seg[:, 0]], 1)        # interior side for rim->hole order
    out = []
    for i in range(len(curve)):
        if i == 0: n = nrm[0]
        elif i == len(curve)-1: n = nrm[-1]
        else:
            n = nrm[i-1] + nrm[i]
            n /= np.linalg.norm(n)
            n = n / max(np.dot(n, nrm[i]), 0.35)
        out.append(curve[i] + d*n)
    return np.array(out)

def cut_between(curve, z0, z1):
    """Sub-polyline of a z-monotone curve between heights z0..z1 (z1=None -> end)."""
    out = []
    zs = curve[:, 1]
    def interp(zq):
        for i in range(len(curve)-1):
            a, b = curve[i], curve[i+1]
            if (a[1]-zq)*(b[1]-zq) <= 0 and a[1] != b[1]:
                t = (zq-a[1])/(b[1]-a[1]); return i, a + t*(b-a)
        raise ValueError("z %.2f not on curve" % zq)
    i0, p0 = interp(z0) if z0 > zs[0] else (0, curve[0])
    out.append(p0)
    if z1 is None:
        out += list(curve[i0+1:])
    else:
        i1, p1 = interp(z1)
        out += list(curve[i0+1:i1+1]); out.append(p1)
    return np.array(out)

def u_at_z(curve, z):
    """Fractional vertex index where a z-monotone curve first reaches height z."""
    for i in range(len(curve)-1):
        a, b = curve[i], curve[i+1]
        if (a[1]-z)*(b[1]-z) <= 0 and a[1] != b[1]:
            return i + (z-a[1])/(b[1]-a[1])
    raise ValueError("z not on curve")

def at_u(curve, u):
    i = min(int(np.floor(u)), len(curve)-2); f = u - i
    return curve[i] + f*(curve[i+1]-curve[i])

def sub_u(curve, u0, u1):
    """Polyline from fractional index u0 to u1 (u0 < u1). Offset curves share
    indices with the outer profile, so equal u = points on the same wall normal."""
    pts = [at_u(curve, u0)] + [curve[i] for i in range(int(np.floor(u0))+1, int(np.ceil(u1)))] \
          + [at_u(curve, u1)]
    return np.array(pts)

def r_at_z(curve, z):
    return cut_between(curve, z, z + 1e-6)[0][0]

# ------------------------------------------------------------------ meshing
def area(poly):
    x, y = poly[:, 0], poly[:, 1]
    return 0.5*np.sum(x*np.roll(y, -1) - np.roll(x, -1)*y)

def clean(poly):
    keep = [poly[0]]
    for q in poly[1:]:
        if np.linalg.norm(q - keep[-1]) > 1e-6: keep.append(q)
    if np.linalg.norm(keep[0]-keep[-1]) < 1e-6: keep.pop()
    poly = np.array(keep)
    return poly if area(poly) > 0 else poly[::-1]

def ear_clip(poly):
    idx = list(range(len(poly))); tris = []
    def cross(o, a, b): return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    guard = 0
    while len(idx) > 3 and guard < 100000:
        guard += 1; found = False
        for k in range(len(idx)):
            i0, i1, i2 = idx[k-1], idx[k], idx[(k+1) % len(idx)]
            a, b, c = poly[i0], poly[i1], poly[i2]
            if cross(a, b, c) <= 1e-12: continue
            ok = True
            for j in idx:
                if j in (i0, i1, i2): continue
                p = poly[j]
                if cross(a, b, p) >= 0 and cross(b, c, p) >= 0 and cross(c, a, p) >= 0:
                    ok = False; break
            if ok:
                tris.append((i0, i1, i2)); idx.pop(k); found = True; break
        if not found: raise RuntimeError("ear clipping failed")
    tris.append(tuple(idx))
    return tris

def revolve(poly, a0=0.0, a1=360.0, seg_deg=1.0):
    poly = clean(poly)
    full = abs(a1 - a0) >= 360 - 1e-9
    n = max(3, int(round(abs(a1-a0)/seg_deg)))
    angs = np.radians(np.linspace(a0, a1, n + (0 if full else 1), endpoint=not full))
    m = len(poly); tris = []
    def V(k, i):
        a = angs[k % len(angs)] if full else angs[k]
        r, z = poly[i]; return (r*np.cos(a), r*np.sin(a), z)
    steps = n if full else n
    for k in range(steps):
        k2 = (k+1) % len(angs) if full else k+1
        for i in range(m):
            j = (i+1) % m
            A, B, C, D = V(k, i), V(k, j), V(k2, j), V(k2, i)
            tris += [(A, C, B), (A, D, C)]
    if not full:
        cap = ear_clip(poly)
        for (i, j, k) in cap:
            tris.append((V(0, i), V(0, j), V(0, k)))                # start cap
            tris.append((V(n, i), V(n, k), V(n, j)))                # end cap
    return np.array(tris)

def fix_orientation(tris):
    v = np.einsum('ij,ij->i', tris[:, 0], np.cross(tris[:, 1], tris[:, 2])).sum()/6
    return (tris[:, [0, 2, 1]], -v) if v < 0 else (tris, v)

def write_stl(path, tris):
    tris, vol = fix_orientation(tris)
    with open(path, "wb") as f:
        f.write(b"shade".ljust(80, b" ")); f.write(struct.pack("<I", len(tris)))
        for t in tris:
            n = np.cross(t[1]-t[0], t[2]-t[0]); l = np.linalg.norm(n); n = n/l if l else n
            f.write(struct.pack("<12fH", *n, *t[0], *t[1], *t[2], 0))
    return vol

def translate_to_bed(tris):
    tris = tris.copy()
    mn, mx = tris.reshape(-1, 3).min(0), tris.reshape(-1, 3).max(0)
    tris[..., 0] -= (mn[0]+mx[0])/2; tris[..., 1] -= (mn[1]+mx[1])/2; tris[..., 2] -= mn[2]
    return tris, mx - mn

# ------------------------------------------------------------------ build
def build(p):
    os.makedirs(p["out"], exist_ok=True)
    t, g, tb, L = p["wall"], p["gap"], p["joint_t"], p["joint_len"]
    O  = outer_profile(p)
    I  = offset(O, t)
    Ig = offset(O, t + g)
    B  = offset(O, t + g + tb)
    tag = f'{p["style"]}_{p["diameter"]:.0f}mm'
    parts, profiles = [], {}

    if p["diameter"] <= p["one_piece_max"]:
        prof = np.vstack([O, I[::-1]])
        parts.append((f"{tag}_one_piece", revolve(prof, seg_deg=p["seg_deg"])))
        profiles["one_piece"] = prof
    else:
        # seam height where the outer surface reaches max_piece diameter
        zz = np.linspace(O[1, 1], O[-1, 1], 4000)
        zs = next(z for z in zz if z - L > O[1, 1] + 15 and
                  max(r_at_z(O, z), r_at_z(Ig, z - L)) <= p["max_piece"]/2)
        # hub: wall above seam + internal sleeve reaching down below seam
        u_top = u_at_z(Ig, zs + 3.0)        # where the sleeve blends into the hub wall
        hub = np.vstack([cut_between(O, zs, None),
                         sub_u(Ig, u_top, len(Ig)-1)[::-1],
                         sub_u(B, u_at_z(B, zs - L), u_top)[::-1],
                         cut_between(Ig, zs - L, zs)])
        ring = np.vstack([cut_between(O, 0, zs), cut_between(I, 0, zs)[::-1]])
        z_lo = O[1, 1] + 3.0
        splice = np.vstack([cut_between(Ig, z_lo, zs - L - 1.0),
                            cut_between(B, z_lo, zs - L - 1.0)[::-1]])
        n = p["ring_pieces"]; d = 360.0/n
        parts.append((f"{tag}_A_hub", revolve(hub, seg_deg=p["seg_deg"])))
        parts.append((f"{tag}_B_rim_segment_x{n}",
                      revolve(ring, -d/2, d/2, p["seg_deg"])))
        parts.append((f"{tag}_C_splice_plate_x{n}",
                      revolve(splice, -p["splice_deg"]/2, p["splice_deg"]/2, p["seg_deg"])))
        profiles.update(hub=hub, ring=ring, splice=splice)
        p["_seam_z"] = zs

    report = []
    for name, tris in parts:
        tris, size = translate_to_bed(tris)
        vol = write_stl(os.path.join(p["out"], name + ".stl"), tris)
        report.append(dict(part=name, size_mm=[round(float(x), 1) for x in size],
                           volume_cm3=round(vol/1000, 1)))
    return O, profiles, report

if __name__ == "__main__":
    import sys
    for a in sys.argv[1:]:                       # e.g. diameter=330 style=cone
        k, v = a.split("="); P[k] = type(P[k])(v)
    O, prof, rep = build(P)
    print(json.dumps(rep, indent=1))
