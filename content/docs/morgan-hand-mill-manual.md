---
title: "Morgan Hand Mill Manual"
weight: 2
draft: false
date: 2026-08-25
---
# The Morgan Hand Mill — Manual Reference

A re-written, factual reference for the **Morgan Hand Mill** — the machine, its
parts, and the taper-setting model — distilled from the Morgan Hand Mill Manual
(chapters A–R, rev. 2005–2013) by **Tom Morgan Rodsmiths** (Tom Morgan & Gerri
Carlson, Manhattan, MT).

> **Note.** This page is a **derived, factual digest** — specs, procedures, and
> the taper-setting model summarized in my own words for reference and education.
> The manual itself is copyrighted and is **not** reproduced here. Source machine
> and maker contact: [troutrods.com](https://www.troutrods.com)
> ([archive](https://web.archive.org/web/2024/https://www.troutrods.com)).
>
> It is the human-readable companion to the caneDNA `mhm_kb.json` knowledge base,
> which grounds caneDNA's Mill Settings and anvil-position visualizer in the
> actual machine.

## What the Machine Is

The Hand Mill is two self-aligning parts: an **adjustable plane** that holds the
cutters, and an **adjustable bed** that holds the strip. The cutters shave both
sides of a strip at once at a fixed bevel; the **taper is set by the bed**, which
raises the strip into the cutters station by station. The plane follows the
grain rather than fighting it.

The redesigned plane (2004, developed with Dennis Detloff) has shipped since late
2005 and adds an adjustable hard stop (from Joe Byrd) that repeats the finish
depth for every strip.

```goat
        plane (holds cutters, rides the base)          hard stop
        +-----------------------------------+          |
        |    o   o   cutter head   o   o     |=========[|]
        +-----------------------------------+
   ======================================================   <- strip on anvil
   |   anvil (supports strip only)                      |
   +----------------------------------------------------+
   |   adjustable bed (push/pull screws set the taper)  |
   +----------------------------------------------------+
   |   base (chrome-plated reference bar)               |
   +----------------------------------------------------+
        ^                                          ^
        bed raised at each 5-in station        bolted to aluminum angle
```

## The Base

| key        | value                                                              |
|------------|--------------------------------------------------------------------|
| what       | Chrome-plated cold-rolled steel bar the plane rides on — the taper reference surface |
| dimensions | 5/8 × 1¾ × 72¾ in                                                   |
| mounting   | Bolts to a 2 × 2 × 3/8 in, 75 in aluminum angle at **7 points** (idea from John Miller) so accuracy doesn't depend on bench flatness |
| capacity   | Two-piece rods up to ~9 ft and various three-piece rods            |

Install the aluminum angle with a slight **~1/8 in upward bow** so the plane
doesn't dip in the middle; check by rocking the plane along the base. The
vertical face has 7 slots on 12-in centers for the anchor screws.

## The Adjustable Bed

A steel bar sitting on top of the base, raised above it by push/pull screws every
5 in to set the taper. The anvil sits on the bed; the strip sits on the anvil.

| key        | value                                                              |
|------------|--------------------------------------------------------------------|
| dimensions | 5/8 × 3/4 × 68 in                                                  |
| stations   | **#0 through #13** (14 stations) on 5-in centers, spanning 0–60 in |
| station #0 | No adjusting screw, only a locking screw — always held tight against the base |
| push screw | 5/16-18 flat-head set screws                                       |
| pull/lock  | 1/4-20 cap-head screws (bed attaches to base with 14 of these)     |

To set a taper: loosen the cap-head (pull) screw, turn the hex-head (push) set
screw in or out to change the bar gap. **Do not over-tighten** — it warps the
bed. Never adjust the bed by more than **0.020 in between adjacent 5-in
stations** or you may permanently damage it (matters for 3-piece / spey shim
setups).

## The Anvils

Anvils are white **HDPE** with embedded brass inserts. Critically, **anvils only
*support* the strip — they do not set the taper** (the bed does), so they don't
wear as the taper changes.

- **5 anvils shipped:** butt-roughing, tip-roughing, butt-finishing, and two
  tip-finishing.
- **Hold-down stations:** finishing anvils have **11 lettered (A–K)** positions;
  roughing anvils have **3** (long / medium / short — short is for ~3-piece rods).
- **Top widths (finishing):** tip ~0.150 in, butt ~0.225 in.
  **Top widths (roughing):** tip ~0.175 in, butt ~0.225 in.
- **Truing:** finishing anvils must be shaved flat between stations (with a
  carbide insert in the dial-holder/shaver) before use — target ±0.001 in
  (0.002 in TIR). **Never recut the factory-installed reference anvil.** Never
  mill an anvil narrower than the smallest strip.

### The A–K Hold-Down Letters & the Mill Stop

The base has tapped holes on its right front labeled **A–K**; matching letters
are stamped on the bed just below the finishing anvils' 11 hold-down screws. A
movable **mill stop** screws into one lettered hole and does two jobs: it stops
the plane so the cutters can't hit the strip's hold-down screw, and it gives an
automatic plane stop matched to the rod section's length.

**Selection rule.** The strip's **tip always anchors between bed stations #12 and
#13** (as close to #13 as possible) so the anvil stays widest at its tip. Choose
the mill-stop letter from the bamboo hold-down screw's position: set the mill so
the cutters just clear the hold-down screw, then mount the stop just behind it —
**in most cases the mill-stop letter equals the hold-down letter.** Untapered
rough cutting uses **hole A** (rightmost).

> **Worked example (7 ft rod).** The strip is fastened in **hole D** (4th from the
> right), putting the ferrule/tiptop point at station #12 with ~3 in of strip past
> it; the butt taper is set from station #3 (stations #2/#1/#0 left at zero).

For one-piece rods on the extension bed, use **hole B** for rough/finish butt and
**hole A** for finish tip. Short (3-piece) sections may anchor farther up the
anvil for support.

## Cutter Heads

Swappable heads for 8-, 6-, 5-, or 4-strip rods (**6-strip is standard**).

| head     | included angle | hold-down shoe angle |
|----------|---------------:|---------------------:|
| 8-strip  | 46°            | —                    |
| 6-strip  | **61.5°**      | 61.5°                |
| 5-strip  | 73.5°          | 73.5°                |
| 4-strip  | 92°            | 91.5°                |

Morgan uses **61.5°** for 6-strip (not the traditional 60°), per Winston
practice, to reduce visible glue seams.

**Inserts.** Two carbide inserts, 3 edges each; a set planes ~3–5 rods. Cut depth
≤ 0.010 in/pass green, 0.001–0.003 in/pass heat-treated. Regular inserts are
TPGW-321, 3/8 in inscribed circle, 0.015 in tip radius; since July 2011 supplied
inserts are C5 carbide (harder), 15% relief, TiN-coated relief edge, diamond-lapped
top. Install with tops parallel to the pocket; rotate/pair inserts to double edge
life.

## The Measuring Block

A caliper-mounted 6061-T6 aluminum block that reads strip **height** in
per-geometry grooves. Calibrate with a **#38 drill blank (0.100 in)**.

| groove        | constant (drill height) |
|---------------|------------------------:|
| 61+ (6-strip) | 0.152 in                |
| 73+ (5-strip) | 0.140 in                |
| 91+ (4-strip) | 0.123 in                |

Add 0.100 / 0.200 in when a strip exceeds 0.100 in. Glue up ~6 measured sections
to verify your own constants, since glue and pressure shift results slightly.

## The Taper-Setting Model

This is the heart of the machine, and the part most often confused.

> **Two separate steps.**
> 1. **Set the taper.** Using the plane's dial indicator, raise the bed at each
>    5-in station to the correct height above the base.
> 2. **Mill.** Measure the **strip height** with calipers / the measuring block
>    as you cut, and stop at target. The hard stop then repeats that depth for
>    every strip.

- **The station "setting" is** the cumulative rise of the bed at each station
  relative to a chosen reference (typically **#2 = 0.000**). It equals
  *(half-dimension at reference) − (half-dimension at that station)* =
  caneDNA's `total_increase`. **It is not the strip height.**
- **The strip height is** half the flat-to-flat rod dimension at that station
  (one strip). It is **measured during milling, never set by the bed**.
- **Reference station.** Register the taper so the strip tip is near the anvil
  tip; for shorter rods start the taper at station #2 (or higher), not #0/#1, to
  avoid cutting the anvil too narrow at its tip.
- **Extend past length.** Continue the taper one or more stations past the rod's
  end so strips have extra length for straight gluing (Morgan likes ≥ 5–6 in
  extra; min 3 in on tips).

### The Plane's Dial

Calibrated dial reads 0–50 in 0.002-in steps; **one revolution = 0.050 in of cut
depth** (clockwise lowers). Dial indicator travel is 0–1 in at 0.001 in accuracy.
A dovetail slide + gib runs the plane; backlash is removed by a spring-loaded
Teflon plug (**never remove it**). Nylon side pads (moly-impregnated) let it
slide — set them 0.628–0.629 in apart with the supplied jig.

> **RodDNA caveat (from manual chapter J).** Of RodDNA's MHM Settings Report, use
> the **Station #, Increment, Rod Dim, and Increase** columns; **disregard "Form
> Depth"** (should be strip height) **and "Settings"** (wrong on some tapers).
> This is why caneDNA computes `strip_depth` + `total_increase` itself rather
> than porting RodDNA's report. Free taper sources with Hand Mill station
> settings: [RodDNA.com](https://www.roddna.com) and
> [hexrod.net](https://www.hexrod.net) (Frank Stetzer, with Chris Obuchowski).

## Workflow, End to End

**Split → prep / straighten nodes → drill anvil hole → rough cut (taper preset) →
swap anvil → finish anvil, set taper, finish cut in many light passes.**

Always mill **butt → tip**, and mark the butt end. Grip *behind* the adjusting
head (never on it) with centered downward pressure; take many light passes and
re-cut the first 2–3 in of each pass to full depth.

### Strip Preparation

- Buy ≥ 10 poles (ideally 20+). Reject deep cuts, big dark splotches, and node
  heat marks; power fibers must run the full glued-section depth.
- Wall thickness: **butt 5/16–1/2 in, tip 3/16–5/16 in.**
- Node spacing: **butt 9–14 in, tip 14–20 in.** Common three/three node match;
  avoid nodes at cut ends, ferrules, and tiptop.
- Straighten with heat (gun 350–450 °F) and remove twist, especially the first
  18 in of butts; square or slightly inward-taper the strip sides.
- **Heat-treat to light brown** (raises MOE, resists set); *black = brittle.*
  Remove maximum material before treating (harder afterward); rest treated
  strips ≥ 1 week to regain moisture.
- Rough sections **≥ 6 in over finish** (+~2 in on the butt for the anvil screw);
  split ~1/8 in wide.

### Milling

- **Rough** on a wide roughing anvil (strip + mill stop in hole A) to a 61.5°
  bevel just wider than the anvil; mount the hold-down shoe once an apex forms.
  The stainless, spring-loaded **hold-down shoe** mounts in the head's center
  hole and rides *ahead* of the cutters, so it doesn't affect accuracy — critical
  for slender tips and stiff quad strips. Clean it with alcohol / dry graphite
  only (never oil).
- Then switch to a **finishing anvil** and set the taper.
- **Measure strip height** three ways: micrometer + height/width chart,
  thread-wrapped strips, or the aluminum measuring block (most accurate). Don't
  measure the apex directly (leftover "fuzz").
- **Finish in two stages:** cut ~0.015 in oversize, then install fresh sharp
  cutters and finish at **0.001–0.002 in/pass**. Remove apex fuzz before gluing
  and saw off the thick held-down butt.
- Minimum strip width: **tip 0.200 in / butt 0.250 in.** Tip hold-down 2-56 (#43
  drill), butt hold-down 4-40 (1/8 in), hole ~1 in from the butt.

> **7 ft #4 wt example (#12 ferrule):** strip height 0.096 in at the ferrule
> (station #12), 0.033 in at the tiptop.

## Accessories

| accessory                | what it does                                                        |
|--------------------------|---------------------------------------------------------------------|
| **Hollow fluting cutter**| Hollows strip centers to cut weight (Stoner/Winston cross-section). Rollers 64/76/94° (64 std for 6-strip). Suggested wall 0.070 in (trout) / 0.085 in (steelhead-salmon). Leave the rod **solid under ferrules** with a ~2.5 in transition; hollow after finish-cutting, butt→tip. Hollowing loses stiffness — increase section area ~2–5% to compensate. |
| **Swelled butt kit**     | Shims to raise the finishing anvil for a swelled butt. **Max swell 0.060 in per strip / 0.120 in finished — do not exceed** (anvil damage). 100 shims (0.060/0.030/0.020/0.010 in) combine in 0.020-in steps; initial rise over 2.5 in. |
| **Magic star cutter**    | Alternate hollowing — an inverted-T with central support spokes (width 0.030–0.065 in). Square inserts remove more but leave ~80% of the triangle's glue seam (weaker). Suggested wall 0.060–0.070 in (trout) / 0.075–0.085 in (steelhead-salmon). |
| **Extension bed**        | 36 in bolt-on bed for **one-piece rods up to ~7 ft 6 in**. The strip is cut on *both* finishing anvils, switching once; the tip-butt transition lands between stations #7–#8. Strip length = rod + 4 in tip + 5 in butt + 2 in hold-down (e.g., 7 ft → 95 in). |
| **Enamel scraper**       | 60°-groove anvils (with the dial-holder/shaver) to scrape enamel off beveled strips. The bed must have **no taper** when shaving. |

## Reference & Further Reading

No book covers the Hand Mill itself. The manual recommends:

- Garrison & Carmichael, *A Master's Guide to Building a Bamboo Fly Rod* — the
  amateur's "bible"
- Howell, *The Lovely Reed*
- Maurer & Elser, *Fundamentals of Building a Bamboo Fly-Rod*
- Ray Gould; and the Stoner / McLane encyclopedias

Tom Morgan runs a private owners' list server (join by email via
[troutrods.com](https://www.troutrods.com)). Free taper sources with Hand Mill
station settings (including quads and pentas):
[RodDNA.com](https://www.roddna.com)
([archive](https://web.archive.org/web/2024/https://www.roddna.com)) and
[hexrod.net](https://www.hexrod.net)
([archive](https://web.archive.org/web/2024/https://www.hexrod.net)).

---

*Source: The Morgan Hand Mill Manual (chapters A–R, rev. 2005–2013), Tom Morgan
Rodsmiths. This is a factual reference re-written in my own words; the manual is
copyrighted and not reproduced here.*
