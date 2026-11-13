---
title: "Tower Sourcing in the USA: Pot and Center Pipe"
date: 2026-11-12
weight: 6
---

The [tower](the-tower) is designed around European parts: a 38 × 38 × 40 cm square planter and a **20 mm OD** center pipe. Neither is easy to find in the US. This page collects what builders in the MakerWorld comments (about 1,200 ratings; read through 2026-11-12) actually used, plus my own sizing checks. Claims are marked **(commenter)** where a builder reported them, and **(calc)** where I worked them out from standard sizes. Nothing here has been built or tested by me yet.

## Center pipe (20 mm OD)

The pipe carries water up the middle and, per the designer, also adds stability. It runs through a 20 mm bore in every module, so **anything that sticks out past the OD will not pass**: no welds, rivets, or external couplers.

### What commenters used

| Pipe | Fit | Source |
|---|---|---|
| 20 mm aluminum | Designer's choice; third season, still looks fine | Designer |
| 20 mm stainless | Works | Commenter |
| **3/4" OD vinyl tubing** | 19.05 mm, "worked perfectly" | Commenter |
| 1/2" PEX | Used as the **center** pipe once; mostly used for the 16 mm ring uprights (see below) | Commenters |
| 16 mm aluminum plus a printed 20→16 reducer at the pump | Works but is "a snug fit"; how the 16 mm pipe is centered in a 20 mm bore is not explained | Commenter |
| 16/22 aquarium tubing | One builder says it fits; another says it does not (22 mm OD in a 20 mm hole). Treat as **not working** | Commenters |

### Standard US sizes against the 20 mm bore **(calc)**

| Stock | OD | vs 20 mm |
|---|---|---|
| 3/4" OD tube (aluminum, stainless, vinyl) | 19.05 mm | 0.95 mm under; slides through, a little play |
| 1/2" PEX | 15.9 mm | 4 mm under; needs a shim or sleeve |
| 1/2" PVC / CPVC | 21.3 mm | 1.3 mm **over**; needs shaving (a commenter did not want to) |
| 3/4" PEX | 22.2 mm | Over |

So **3/4" OD tube is the closest US match**. A metric 20 mm tube from a supplier such as McMaster-Carr is another route, but I have not checked stock.

### The aluminum tubes I am considering

Two 3/4" OD, 6 ft candidates. **The Everbilt tube is the better fit**: its thinner wall leaves a 16.6 mm ID, about 70% more flow area than the Grainger tube's 12.7 mm ID **(calc)**, and it is close to the roughly 17 mm ID of a 20 × 1.5 mm tube.

| | Everbilt (Home Depot) | Grainger 795AP1 |
|---|---|---|
| OD | 0.750 in (19.05 mm) | 0.750 in (19.05 mm) |
| Wall | 0.0489 in (1.24 mm) | 0.125 in (3.2 mm) |
| ID | **0.652 in (16.6 mm)** (calc) | 0.500 in (12.7 mm) |
| Alloy | Not stated on the listing | 6061-T6, extruded |
| Length | 6 ft (3 ft and 4 ft also sold) | 6 ft |

[Everbilt 3/4 in x 6 ft aluminum round tube](https://www.homedepot.com/pep/Everbilt-3-4-in-x-6-ft-Aluminum-Round-Tube-Metal-Stock-6712/340451329) ([archive](https://web.archive.org/web/2024/https://www.homedepot.com/pep/Everbilt-3-4-in-x-6-ft-Aluminum-Round-Tube-Metal-Stock-6712/340451329)): specs from a screenshot of the listing (retail page, in stock for store pickup on 2026-11-12). Measure the real OD with calipers; the thinner wall is more flexible, so handle it carefully.

[Grainger 6061 aluminum round tube, item 795AP1](https://www.grainger.com/product/Aluminum-Round-Tube-6061-795AP1) ([archive](https://web.archive.org/web/2024/https://www.grainger.com/product/Aluminum-Round-Tube-6061-795AP1)):

| | |
|---|---|
| Material | 6061-T6, extruded |
| OD | 3/4 in (19.05 mm) |
| Wall | 0.125 in (3.2 mm) |
| ID | 0.5 in (12.7 mm) |
| Length | 6 ft (183 cm) |

Spec as shown on the listing; check the current page before ordering.

- **Length:** a single 6 ft piece means **no joint**. The designer's 180 cm tower includes the pot and the pipe stops 1 cm above the Rainbase, so 183 cm should just do it. Add up your module heights first; a taller build will not fit.
- **OD:** 0.95 mm under the bore. Take up the slack at the pump connector with PTFE tape or heat shrink, or print a connector with a 19.05 mm bore. A loose connector is where leaks start (the designer's fix for leaks there is a sealing ring).
- **ID:** the Grainger tube's 12.7 mm gives roughly **45% less flow area** than a 20 × 1.5 mm tube (about 17 mm ID; the designer's wall thickness is not stated) **(calc)**; the Everbilt's 16.6 mm is nearly the same as that tube. It matters because the pump has to lift water about 1.8 m. Check the pump's **maximum head** against the finished tower height before relying on it; I have not verified the Syncra's head rating.

### If you have to join shorter lengths

Use an **internal sleeve**: a tube that slides inside both ends, 4 to 6 in long, scuffed, degreased, and bonded with two-part epoxy, with the sections butted tight. Welding thin aluminum tube needs TIG and leaves a bead that must be ground flush. Rivets and screws leave heads that snag in the modules. With the Everbilt tube (16.6 mm ID) a 5/8" OD (15.9 mm) sleeve leaves about 0.7 mm of clearance for epoxy. The Grainger tube's 12.7 mm ID is too small for that, so with it just buy the 6 ft length.

### Epoxy and food safety

Cured epoxy is generally inert, but look for **NSF/ANSI 61** (drinking-water components) or **FDA 21 CFR 175.300** compliance on the datasheet for the exact product. Avoid metal-filled putties. Wipe out squeeze-out so no bead is exposed to flowing water, mix at the stated ratio, cure fully (often 24 h or more), and flush the system with plain water before planting. An epoxy-free alternative is a tight press-fit sleeve sealed with 100% silicone sold as aquarium-safe (bathroom silicone often contains mildewcide).

### Aluminum in nutrient solution

One commenter worried aluminum reacts with fertilizer salts at pH 5 to 6.5 and suggested PVC-U or polyethylene. The designer found no evidence against aluminum online and is in their third season with it. Someone else planned a polyethylene pipe (cheap, easy to cut, 10 m coil). If it bothers you, choose stainless or plastic.

### Ring uprights (optional support structure)

The "Rings V4" print profile needs four 1 m uprights of **16 mm OD** pipe. In the US, **1/2" PEX** works (15.9 mm). One builder put a **7/16" wooden dowel** inside the PEX to stiffen it. Copper also fits but is expensive. In Europe the part is sold as "rigid M16 installation pipe".

## Pump

Commenters used the **Sicce Syncra Silent 2.0** (designer's pick), a 700 GPH "WUCIOOO" pump, and a 40 W, 3000 L/h pump. The pump I plan to use:

[VIVOSUN 660GPH submersible pump, size 6"×4"-660](https://www.amazon.com/dp/B097HF98WF) ([archive](https://web.archive.org/web/2024/https://www.amazon.com/dp/B097HF98WF)), from a screenshot of the listing on 2026-11-12:

| | |
|---|---|
| Flow | 660 GPH (2500 L/h), at zero lift |
| Max lift | **8.2 ft (2.5 m)** |
| Power | 35 W |
| Price | $19.99 |
| Extras | Adjustable flow, three barbed adapters, suction-cup feet, detachable body |

- **Lift margin:** the tower needs about 1.8 m of lift, 72% of the pump's max head, so about 0.7 m of margin at shutoff **(calc)**. Actual flow at 1.8 m will be well below 660 GPH, and the pipe's friction takes more. Test it half full as the designer advises and use the flow adjuster if it sprays too hard.
- **Outlet adapters:** three threaded barbs come in the box, **0.5", 0.62" and 0.75"**. None fits inside the 16.6 mm ID pipe, because barb ridges are wider than the nominal size. Use the **0.75" barb** with a 2 to 3 in piece of **3/4" ID flexible tube**, clamped on the barb, with the pipe pushed into the other end. The tube's OD (about 1 in) does not matter because the joint sits below the lid. Do not clamp the pipe end: the pipe has to slide out for cleaning. The flexible tube also forgives a pump that is slightly off-center, but the outlet should still be near **dead center** under the pipe. Use the 0.62" or 0.5" barbs only to throttle flow; their bore sizes are not stated.
- **Cord:** it has a molded plug. Check it fits through the lid's square cable hole before assembly.

## Pot (reservoir)

The designer's requirements: at least 40 L (10 gal), **square**, thick upper rim, **no drain holes**, plastic (polyethylene preferred), drillable rim. The footprint is about 38 × 38 cm.

| Option | Reported by | Notes |
|---|---|---|
| **27-gal storage tote, cut a hole in the lid** | Commenter (BJ's tote) | "Works perfectly." Wider base. Two builders used it. |
| **Two 27-gal totes under a plywood top** | Commenter (4 towers, 2 reservoirs) | Spray-painted the black totes white against heat. Got leaks between layers and at the board; plans silicone between each layer. Plants got crowded at two towers per 4 ft. |
| **Plywood board between base and any pot** | Designer-endorsed (highest-liked tip, 39) | Screw the round or square base to a board, then adapt the board to the pot. One builder clamped it with a gasket. |
| **Step2 Lakewood planter box** | Three commenters | Needs a modified base (STEP and STL shared by commenters in Google Drive). It is a **self-watering planter**; the inner basin cannot be removed, so usable volume is less. One builder refills about every 2 weeks at two 15-minute waterings a day. Hold the base plates carefully; they are tight against the rings. |
| **Allen + Roth 14 in self-watering planter (Lowe's)** | Commenter | Extended the base edges by a few mm; no leaks. |
| **Tusco MSQT23BK square planter (Amazon)** | Commenter | Reported only as purchased. |
| **IKEA Sortera 60 L** | Several EU builders | Needs printed adapter parts (MakerWorld model 1594718). A high-tensile pipe was added to carry weight. I have not confirmed the US IKEA sells it. |

**Avoid:**
- **5-gallon buckets.** The designer says that is too small for a tower this size, and one builder who adapted a thin square pot said the sides bulged when it filled.
- **Galvanized steel cans.** Suggested once in the thread; they would rust in nutrient solution.
- **Thin-walled planters.** One builder found a planter weak where the tower mounts.

Reservoir size matters. One builder says a 40+ L pot lasts about 4 days in summer if filled to the top; another lost track of pH and had to change the water repeatedly.

## Build and print gotchas from the comments

- **Weak tabs.** The joiner tabs on the main body break during printing or later (several builders). Printing with the **BigTower with connector supports** profile helps. Updated V5 profile moves the seam to the middle and slows the speed.
- **Feet failing on GrowSmall4 and Grow8.** The bottom right foot fails on some printers (P2S reports). Changing the **seam to random** fixed one; adding hand-placed supports fixed another.
- **Wet PETG.** Dry PETG first, even new rolls. Several builders say that fixed their failures.
- **Print bed.** The rings do not fit on a 220 × 220 mm bed (K1C); the rest does.
- **Filter flap leaks.** Too thick a foam pad caused it for one builder (thinner pad fixed it). Others used sealing tape, or a **U-shaped** TPU gasket (a flat 0.6 mm gasket made it worse). A "no flap" base option exists in the print profiles.
- **Missing a Big4 pot.** The Grow8 pot with four top connectors has no offset, so with one fewer Big4 pot the rings will not attach (one builder hit this at 2 m tall).
- **Nuts stuck.** An M5 nut jammed and blocked disassembly; embedded or heat-set nuts are suggested.
- **Layer leaks.** Silicone or a seal at each seam if you mount the base to a board (see the four-tower build above).
- **Top rain module arms** failed repeatedly for one P1S owner; the designer asks about brims and infill (use grid, crosshatch or gyroid, not something sparse).

## Growing notes from the comments

- A builder grew **72 strawberries in one tower**; high flow also kept water temperature stable in heat.
- Another runs EC at **1800 to 2200** for fruiting crops. Lettuce and herbs need much lower.
- Rockwool starts, with clay pebbles in the net pot, per the designer. Clay can skew EC and pH readings, and one builder asked for printed inserts instead.
- Several people added **lights**: LEDs built into the support rings, or a taller lid. Files are on other MakerWorld pages (one linked at the designer's invitation).
- PETG is fine in water, and white PETG reflects sun but encourages algae; the top parts are black for that reason.
- **Existing commercial towers:** one builder scaled the model to 86% so their mesh pots and clips fit.

## Shopping check before you buy

- [ ] Pot is square, 10+ gal, no drain holes, drillable rim, or you have a board to adapt it
- [ ] Pump max head is above tower height plus the extra loss from a narrower pipe
- [ ] Center pipe OD is within about 1 mm under 20 mm and has a way to seal at the pump
- [ ] Pump connector matches the pipe OD (printed connector in the print profiles)
- [ ] Epoxy, if used, has an NSF 61 or FDA 21 CFR 175.300 datasheet
- [ ] PETG is dry before printing

## Open questions

- Real flow of the VIVOSUN 660 at 1.8 m lift through the 16.6 mm ID Everbilt pipe (or 12.7 mm ID Grainger), and whether the lift is enough to reach the sprinkler.
- Whether the 3/4" ID tube grips the 19.05 mm pipe snugly enough to seal without a clamp; pot depth minus pump height sets the pipe length and the joint length, so dry fit first.
- Whether the VIVOSUN plug fits the lid's cable hole.
- Alloy of the Everbilt tube (not stated on the listing).
- Whether the printed pump connector can be re-sized for a 19.05 mm pipe, or whether tape is enough.
- Which US pot to use. The 27-gal tote and a plywood adapter is the most reported without custom CAD.
