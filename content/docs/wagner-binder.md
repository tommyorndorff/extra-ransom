---
title: "Wagner-Style Rod Binder"
weight: 45
---

A Wagner-style rod binder uses a continuous drive belt to wrap binding cord around the glued-up hexagonal strip bundle, applying even spiral pressure while the epoxy sets. The design below maximises 3D-printed parts; the baseplate and axle hardware are the only non-printed items.

---

## How it works

```goat
                    cord spool
                         |
                    [cord guide]  <-- binding cord exits here at ~45°
                         |
  drive handle           |
       |                 v
   [drive wheel] --belt--> rod bundle <--belt-- [idler 1]
                              |
                           [cradle]  (two of these, one near each end)
                              |
                         [idler 2]
                              |
                         [idler 3] (keeps belt off cradle, ~170° contact)
```

The drive wheel turns the belt. The belt wraps around the rod bundle, spinning it. The binding cord is fed from the spool through the cord guide onto the spinning rod at roughly 45°, laying down an even helix of wraps as you advance the rod through the cradle.

The key dimensional constraint (from the [Garrison binder notes](garrison-binder)) is that the first idler wheel must be positioned so the belt contacts the rod at **≤170°** — any more and the belt drags on the cradle and causes twists.

---

## Bill of materials

### 3D-printed parts

| Part | Qty | File | Material | Infill |
|---|---|---|---|---|
| V-groove cradle | 2 | [`cradle.stl`](/static/wagner-binder-3d/cradle.stl) | PETG or PLA | 40% |
| Drive wheel | 1 | [`drive_wheel.stl`](/static/wagner-binder-3d/drive_wheel.stl) | PETG | 60% |
| Idler wheel | 3 | [`idler_wheel.stl`](/static/wagner-binder-3d/idler_wheel.stl) | PETG | 40% |
| Cord guide post | 1 | [`cord_guide.stl`](/static/wagner-binder-3d/cord_guide.stl) | PETG or PLA | 40% |
| Spool holder bracket | 1 | [`spool_holder.stl`](/static/wagner-binder-3d/spool_holder.stl) | PETG or PLA | 40% |

PETG recommended over PLA for parts under load (drive wheel, idlers). The drive wheel sees the most stress; print it at 60% infill with 4 perimeter walls.

### Hardware

| Item | Qty | Notes |
|---|---|---|
| Baseboard | 1 | 600 × 100 × 18 mm hardwood or 3/4" plywood |
| Axle bolts M8 × 40 mm | 4 | One per idler (×3) + drive wheel (×1) |
| M8 nyloc nuts | 4 | |
| M8 washers | 8 | Two per axle |
| M4 × 20 mm bolts | 4 | Mount cradles to baseboard (2 per cradle) |
| M4 nyloc nuts | 4 | |
| M6 × 80 mm bolt | 1 | Spool holder axle (cord spool sits on this) |
| M6 washers | 4 | |
| Drive belt | 1 | ~600 mm braided mason's line (see below) |
| Crank handle | 1 | Bent 6 mm steel rod or wooden knob on M8 bolt |
| Weight | 1 | ~400 g — coffee jar + hardware, adjustable |

---

## Printed part details

### Cradle — `cradle.stl`

**50 × 38 × 35 mm.** V-groove: 60° included angle (30° each side from vertical), 15 mm deep, centred.

The 60° groove matches the hexagonal cross-section of the bound strip bundle. The groove depth of 15 mm accommodates butt sections up to ~0.37" (9.4 mm) across flats, which covers most 6–8 wt tapers.

After printing, drill two **4 mm holes** through the base (one near each end, 10 mm from edge, centred on width) for the M4 mounting bolts.

Orient groove-up for printing. No supports needed.

### Drive wheel — `drive_wheel.stl`

**OD 50 mm, width 20 mm.** Belt groove: 5 mm wide × 3 mm deep, centred on the width.

After printing, drill an **8 mm centre hole** through the axle axis. The crank handle threads into or clamps onto this axle.

### Idler wheels — `idler_wheel.stl`

**OD 36 mm, width 14 mm.** Belt groove: 4.5 mm wide × 2 mm deep.

After printing, drill an **8 mm centre hole** through each. Mount with M8 bolts, two washers, and a nyloc nut — snug but free to spin.

### Cord guide — `cord_guide.stl`

**25 × 20 × 30 mm** block with a 6 mm-wide V-notch (8 mm deep) cut into the top. The binding cord rides in the notch under tension, guiding it onto the rod at ~45°.

Mount flush against the front face of the baseboard, roughly centred on the rod path. Adjust fore/aft angle to get the correct approach angle.

### Spool holder — `spool_holder.stl`

**30 × 10 × 55 mm** U-bracket with a 14 mm-wide × 25 mm-deep slot at the top. Drop an M6 bolt through the spool and let it rest in the slot — gravity holds it, and friction from cord draw provides light tension.

---

## Assembly

### 1. Mark out the baseboard

```goat
   |<----------- 600 mm --------->|

   [cradle]  [idler2][idler3]  [drive]  [idler1]  [cradle]
      |          |      |         |        |          |
     100        220    280       370      440        500   (mm from left)
```

These positions are a starting point. The critical adjustment is idler 1 (rightmost): move it until the belt contacts the rod bundle at no more than 170°, measured from the exit point at the drive wheel side. Too far left → belt drags on the cradle and twists the rod.

### 2. Mount the cradles

Bolt each cradle to the baseboard with two M4 bolts, centred left-right. The groove tops should be at the same height — check with a straight edge before tightening.

### 3. Mount the wheels

Drill 8 mm axle holes in the baseboard at each wheel position. Thread an M8 bolt up through the baseboard, washer, wheel, washer, nyloc nut. The wheel should spin freely with no play.

The drive wheel axle gets a crank handle instead of a nut on top.

### 4. Make the drive belt

A knotless braided belt runs smoother than a knotted one. Use ~600 mm of 3/16" braided mason's line:

1. Thread one end through the eye of a large needle, 50 mm deep.
2. Push the needle into the hollow core of the *other* end of the line, 30 mm in, and back out.
3. Pull until the end disappears inside the splice. Stitch to secure.

Route the belt: drive wheel → idler 1 → over the rod bundle position → idler 2 → idler 3 → back to drive wheel.

Hang the weight on the belt between idler 2 and the rod bundle to load the belt against the rod.

### 5. Set up the cord spool

Drop the spool holder bracket onto the baseboard near the cord guide end. Thread the M6 bolt through the spool, rest it in the U-slot. Thread the binding cord through the V-notch of the cord guide.

Check cord tension: with the weight hanging on the belt, the cord should move freely — if you hang the weight on the cord, it should pull easily. Cord tension should be slightly *less* than belt weight; excess cord tension causes twist.

---

## Tuning

- **Rod twists during binding** — cord tension too high, or idler 1 positioned past 170° contact. Fix the idler position first; reduce cord tension second.
- **Belt slips off wheels** — belt groove too loose, or belt not centred. The 5 mm groove on the drive wheel and 4.5 mm on the idlers has about 0.5 mm clearance for a 3/16" (4.8 mm) cord belt; if using a thinner belt, shim with tape.
- **Uneven wrap spacing** — rod advance speed inconsistent. Try taping a spacing guide to the baseboard.
- **Cradle marks the rod** — too much weight on the belt. Start at 400 g (butt sections) and reduce until marks disappear. Tip sections need less weight.

---

## Print settings

All parts can be printed on a standard FDM printer with a 0.4 mm nozzle.

| Setting | Value |
|---|---|
| Layer height | 0.2 mm |
| Perimeter walls | 3 (drive wheel: 4) |
| Top/bottom layers | 4 |
| Infill | 40% gyroid (drive wheel: 60%) |
| Supports | None required |
| Bed temp (PETG) | 80°C |
| Nozzle temp (PETG) | 235°C |

---

## Related

- [Garrison Binder](garrison-binder) — the design this is adapted from; detailed notes on tuning
- [Rod Binder Notes](rod-binder-notes) — Smithwick binder and additional references
