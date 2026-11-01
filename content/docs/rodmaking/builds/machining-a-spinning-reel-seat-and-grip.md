---
title: "Machining a Spinning Reel Seat and Building a Grip"
date: 2026-11-01
weight: 250
aliases:
  - /docs/rod-builds/machining-a-spinning-reel-seat-and-grip/
---

A plan and procedure for making the handle hardware of
[Rod 002, the 6'6" French Broad spinning rod](/docs/rodmaking/builds/002-french-broad-spinning-rod/)
myself: a **machined reel seat** (fixed hood plus a sliding threaded ring)
and a **cork grip** built around it. The build log already covers two
handle options: cork with two sliding rings (Option A) and a Fuji VSS
skeleton seat on an arbor (Option B). This page is a third option: turn the
seat from bar stock instead of buying it.

> **Status: plan only.** Nothing here has been cut yet. The cane for Rod 002
> hasn't been milled either. Anything I haven't measured or confirmed is
> marked **to confirm**, and every dimension below is a starting point, not a
> result.

## What the repo does and doesn't confirm

| Item | Status |
|---|---|
| Rod: 6'6", 2 pc, hex, light / moderate-fast, 1000-size reel | Confirmed (build log) |
| Blank under the grip: **0.279–0.281″** (7.09–7.14 mm) | Confirmed (build log spec table, taper table) |
| Reel-foot center about **8.5″ from the butt**; 12″ cork handle in Option A | Confirmed as Option A's design value; still to be fine-tuned by balance |
| Fuji VSS 16 seat: 120 mm long, 13.0 mm ID (the graphite-blank option) | Confirmed (build log, and re-checked on [Mud Hole's VSS page](https://mudhole.com/products/fuji-vss-standard-versatile-spinning-reel-seat)) |
| A cork-ring press exists as a printable tool | Confirmed ([printable rod tools](/docs/rodmaking/printable-rod-tools/)) |
| Owning a **metal lathe** or **mill** | **Not stated anywhere in the repo** (`equipment.md` is a stub; no page mentions a lathe). **To confirm.** |
| The reel's foot dimensions | **To confirm.** Measure the actual reel. |
| Thread size for the seat | **My choice, not a standard.** See [Threads](#threads). |

If I don't have a lathe, the fallback is Option A or B from the build log.
Those need no machining. A wood lathe (or a drill with a support stand) is
enough for the grip alone.

## Choosing the style

| Style | How it holds the reel | Pros | Cons | Fit for Rod 002 |
|---|---|---|---|---|
| **Sliding rings on cork** (Option A in the log) | Foot sits on bare cork, two rings slide over the ends | Lightest; period-correct; no hardware | Rings can creep when wet and cold | Recommended in the log |
| **Fixed hood + threaded ring** (this page) | Foot sits in a fixed hood; a threaded ring winds up against the other foot | Locks solid; no creep; adjustable to the reel | Needs machining and exact thread fit | The one planned here |
| **Hood and cap, no thread** (slip-on sliding band) | Same as the sliding rings but with metal-to-metal hoods | Simple to make | Same creep problem as rings | Skip |
| **Bought skeleton seat** (Fuji VSS 16, Option B) | Fixed hood plus a threaded hood and lock nut | Cheap, tested, ~$6 | Looks modern on cane; needs an arbor | Fallback |

A **screw-lock** seat (what the machined design is) beats a sliding band on
a spinning rod because the reel foot takes the full pull of a hooked fish
and the casting hand squeezes the seat. The band-only style is fine for
light fly-style reels but is the one more likely to loosen.

## Spinning-specific geometry

```goat
 tip                                                         butt
 --------+-+----------+------------------+----------+---------+
  blank  | | foregrip | fixed hood  foot | threaded | rear    |
 --------+ | (cork)   |  [==== foot ====]|  ring    | grip    |
         +-+----------+--------+--+------+----------+---------+
                               |  | stem
                            .--+--+--.
                           |  reel    |
                            '--------'
```

- **The reel hangs below the seat.** The foot channel is open on the
  underside. The seat is a tube with a flat-bottomed (or slightly dished)
  cradle where the foot sits, a fixed hood at one end, and a threaded ring
  at the other that pulls the second foot tight.
- **Seat body OD: 7/8″ to 1″** (22–25 mm) is the usual range for finished
  spinning seats and the size my hand is likely to want on a light rod.
  Finished seat sizes vary by maker, so I'll settle on a diameter from the
  reel and my grip (**to confirm**).
- **Reel foot gap.** The distance between the fixed hood and the threaded
  ring at full open must exceed the foot-to-foot length of the reel, and at
  full closed must be less than the foot length. I'll measure the 1000-size
  reel I'm going to use with calipers (**to confirm**) and make the
  channel about 1/4″ longer than that with the threaded ring's travel at
  least that much.
- **Hex under a round bore.** The butt is **0.279–0.281″ across flats**, so
  the corners are 0.281 / cos 30° = **0.325″** (8.24 mm). A round bore
  smaller than that cuts into the corners. Mill the bore to clear the corners,
  or ream the bushing bore to the corner diameter and fill the gap (see
  [Bushings](#bushings-and-bonding-to-the-blank)).

## Materials

| Material | Pros | Cons | Notes |
|---|---|---|---|
| **6061-T6 aluminum** | Easy to turn; light; anodizes well; good thread life | Needs finishing to look right; will gall on its own threads if both parts are bare | My default pick |
| **Brass (360 free-machining)** | Cuts beautifully; classic look on cane; heavy | Heavier on a light rod; tarnishes unless lacquered | Good for the threaded ring only |
| **Stabilized or dense wood body with brass hardware** | Warm look; light | Wood threads wear; moisture movement | Use only for the body, with a metal insert for the threads |
| **Nickel-silver** | The traditional bamboo-rod hardware | Costly; harder to find in bar | Not planned |

Mixing the two (aluminum body, brass ring) avoids galling, because like
metals tend to seize on fine threads. Anodize or lacquer the finished
parts; see [Finishing](#finishing).

## Measurements

All values are design targets, **to confirm** against the reel, the blank,
and a test-fit.

| Feature | Target | Notes |
|---|---|---|
| Blank under the seat | 0.279–0.281″ across flats; **0.325″** across corners | From the build log; measure the real cane |
| Bore of the seat body | blank corners + clearance: **0.340–0.350″** | Or bore to a bushing's OD |
| Bushing OD / ID | OD matches the seat bore; ID matches the tapered cane | Cut from stock or build up from tape and epoxy |
| Seat body OD | **0.875–1.000″** (22–25 mm) | Pick from the reel and grip |
| Wall thickness | ≥ 0.20″ at the thread root | Check after the thread is cut |
| Thread | **1″-20 UNEF, as a design choice** (see below) | Not a published reel-seat standard |
| Thread length on the body | about 0.75″ | 12–15 turns at 20 tpi |
| Reel foot channel | foot length + about 0.25″ | **Measure the reel** |
| Fixed hood height | about 0.12–0.15″ above the foot bed | **To confirm** against the foot |
| Reel-foot center from butt | about 8.5″ | From Option A in the log; adjust by balance |
| Total seat length | about 4.0″ | Hood + channel + ring travel |
| Fit tolerances | thread: class 2A/2B; bore: ±0.002″ | Reasonable shop targets |

## Threads

I didn't find a published thread standard for spinning reel seat nuts.
Manufacturers' product pages (the Mud Hole pages I read) list length, ID,
and OD but not the thread pitch, and different makers use different threads.
So a machined seat can't borrow a standard; I choose my own and both mating
parts are mine.

- **Pick a common machinist thread** so the tooling is on hand: 1″-20 UNEF
  (1″ major diameter, 20 tpi) is a good candidate for a ~1″ body. The
  thread depth is about 0.0325″, so the wall stays healthy. **To confirm**
  against the taps, dies, and single-point inserts I actually own.
- **Cut the male thread on the lathe** (single-point, with the lathe geared
  for 20 tpi) rather than with a die. A die on 1″ aluminum cuts a rough
  thread and leaves it off-center. Take light passes and use cutting fluid.
- **Cut the ring's female thread on the lathe too** (boring bar or internal
  threading insert), then **fit it to the body** by sneaking up on the
  thread: stop when it runs freely with no radial shake.
- **Add relief** at the end of the thread, so the ring can run up against
  the shoulder without bottoming on a half-cut thread.
- **Lock it:** a thin nylon washer or a small O-ring under the ring's face,
  or a second lock ring, so it doesn't back off. **To confirm** which works.

## Machining sequence

This is general machinist practice. I haven't followed an opened reference
for it (see [Sources](#sources)), so treat it as a plan to be checked on
scrap first.

**Lathe**

1. Cut bar stock (6061, about 1.25″ diameter, 5″ long) with about 1/2″ extra.
2. Chuck it, face the end, and **drill and bore through** to the bore
   diameter. Bore first so the bore and the outside are concentric.
3. Put the body on a mandrel (or chuck on the bore) and turn the outside to
   OD, leaving a shoulder for the fixed hood.
4. Turn the thread relief, then **single-point the male thread**.
5. Part off. Flip, face to length.
6. Turn the **threaded ring**: bore, internal thread, then knurl or a hex
   OD if I want grip.
7. Test-fit the ring on the body. Fit it before any other cuts.

**Mill (if available)**

1. Cut the **foot channel**: a flat-bottomed slot across the bed width, with
   a ball-end or corner radius to match the foot.
2. Open the **underside window** so the reel foot can sit on the cane or
   bushing side.
3. Drill any **vent or pin holes** (a small hole to relieve epoxy, and any
   set-screw I want).

**If I don't have a mill:** cut the channel on the lathe with a slotting
setup, or file it by hand with a jig. **To confirm.**

## Finishing

| Option | Pros | Cons |
|---|---|---|
| **Hard-coat or color anodize (aluminum)** | Tough; many colors | Needs a vendor or a home kit; coat is thick, so the threads must be cut oversize/undersize to allow for it (**to confirm** with the anodizer) |
| **Bead-blast, then clear lacquer** | Easy; matte look | Wears at the thread |
| **Polish (brass)** | Classic on cane | Tarnishes; needs lacquer or regular wax |
| **Leave bare, clear-coat only on non-thread surfaces** | Works | Needs periodic cleaning |

Anodizing adds a few ten-thousandths per surface, so cut the threads and
fit them **before** anodizing, then re-check the fit. Masking the threads
during anodizing is the usual alternative.

## Bushings and bonding to the blank

1. **Fit the seat to the cane first, dry.** Slide the seat over the butt.
   It should go on freely at the corners with no rocking.
2. **Make bushings** (two, one at each end of the seat): aluminum or brass
   rings, or turned from epoxy-filled phenolic, with a bore that matches the
   cane's taper at that point and an OD that matches the seat bore. Where
   the bore is round and the blank is hex, either fill the gaps with
   thickened epoxy or turn tape-and-epoxy bushings in place.
3. **Mask** the cane above and below the bonding area, and the seat's
   threads and channel, with painter's tape.
4. **Epoxy** with a slow-cure (30-minute or longer) 2-part epoxy. `equipment.md` records a recommendation of 3M DP2216 for ferrule glue; I
   could use the same adhesive here (**to confirm** it suits an aluminum-to-cane bond;
   the repo only recommends it for ferrules). Use a thin film, and keep it
   off the threads.
5. **Align** the seat so the reel hangs on the same side as the guides, then
   hold it square with the blank for the cure. A tape alignment mark on the
   butt helps.
6. **Wipe** squeeze-out with denatured alcohol before it gels.

## The grip

### Cork rings vs. shaped cork

| Option | Pros | Cons |
|---|---|---|
| **Cork rings, glued up and turned** | Cheap; pick the best rings for the high-touch spots; any shape | Takes time; voids need filling |
| **Pre-shaped cork grip** (the Option B parts in the log: Fuji split fore/rear grips) | Ready to ream and glue | Limited shapes; sized for a particular seat |

I'm using rings here since the machined seat doesn't match a commercial grip.

### Ring dimensions and count

- **Standard ring: 1 1/4″ OD, 1/2″ thick, 1/4″ bore.** That's the size
  Mud Hole's overstock cork rings list ([page opened](https://mudhole.com/products/overstock-cork-rings-25-id)).
  Sizes and grades vary by maker; the "grade" label is a seller's, not a
  standard.
- **Rear grip: 7″ is the build log's choice** for the Option B rear grip,
  about **14 rings** at 1/2″. **To confirm** for this rod (the handle is
  12″ total in Option A).
- **Foregrip: about 3.75″** (as in the log), about **7-8 rings**.
- A 1 1/4″ ring leaves about 0.125–0.25″ for shaping around a 1″ seat, so
  grips that are bigger than the seat are possible but not by much.
  Larger rings exist; **to confirm** stock.
- Buy a few extras and **hand-pick**: put the best rings where the thumb and
  palm sit, and the worst at the ends where washers dent them.

### Glue-up

1. **Bore each ring** to just under the blank (a tapered rattail file or
   reamer on a drill) and put them on a **waxed mandrel** or threaded rod.
   Rings arrive with a 1/4″ bore; the cane is 0.28–0.33″ at the grip, so
   ring bores should be opened slightly.
2. **Glue sparingly.** Enough that the inner surface just shines; excess
   glue forces epoxy onto the mandrel and the grip's outside, and the grip
   can become nearly impossible to remove.
3. **Press the stack**: washers and nuts on threaded rod, or the printable
   [cork press](/docs/rodmaking/printable-rod-tools/#cork-press) from this
   site. Tighten until glue just oozes between the rings.
4. **Put a low-grade ring at each end** to absorb the press marks.
5. **Cure fully**, overnight and a bit more. Reaming too soon makes the
   grip come apart.

### Turning and shaping

- On a **lathe** or a drill with a support stand: true the stack to a cylinder
  with 60-grit on a flat board, then rough the profile, leaving a little
  extra, then work up through the grits. One builder ends at **320 grit**.
- **Shaping without a lathe**: fold sandpaper into a firm corner and work
  wells into the spinning grip; a rasp for the first roughing.
- **Calipers** at the high points; stop slightly above the final diameter.
- **Dust:** cork dust is fine and gets everywhere. Work outdoors or with a
  shop vacuum at the grip.

### Fitting and fill

- **Remove the grip from the mandrel** by gripping it with both hands and
  striking the mandrel on a flat, solid surface.
- **Ream** to the blank and **test-fit**, then bond with epoxy, as with the
  seat. Put the rear grip on first against the seat's rear edge and the
  foregrip against the fixed hood.
- **Fill voids** after shaping and before the final sanding: a cork dust and
  epoxy (or wood-filler) paste, pushed in, left proud, sanded flush.
- **Burnish** with a hard smooth surface or a very fine paper (400-grit or
  finer) to close the surface. (General practice, not from a cited source.)
- **Winding check** (in the log's Option B notes: for a roughly 7.3 mm
  blank): fit at the front of the foregrip, then wrap and finish.
- **Finish:** leave the cork bare or seal it lightly, per taste. **To
  confirm.**

## Parts and materials

| Qty | Item | Notes |
|---:|---|---|
| 1 | 6061-T6 aluminum round bar, about 1.25″ x 5″ | For the body |
| 1 | Brass bar (360), about 1.25″ x 2″ | For the threaded ring, optional |
| 2 | Bushings (aluminum, brass, or tape-and-epoxy) | Sized to the cane at the seat |
| 20–25 | Cork rings, 1 1/4″ x 1/2″ x 1/4″ | Spare rings for matching and for voids |
| 1 | Waxed mandrel or threaded rod, about 5/16″ | Matches the bore after reaming |
| 1 | Rattail file or tapered reamer | For opening the ring bores |
| — | Sandpaper, 60 to 320 grit, and a flat board | Hand shaping |
| — | 2-part slow-cure epoxy | Seat bonding and grip bonding |
| — | Wood glue (Titebond II or similar) | Ring-to-ring |
| — | Painter's tape, denatured alcohol, nylon washer or O-ring | Masking, cleanup, ring lock |
| — | Winding check | Per the log |
| — | Anodize or lacquer | Finish |

**Tools:** lathe with single-point threading and a boring bar (**to
confirm I have this**), calipers, a thread gauge, optionally a mill, the
printed cork press.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Ring binds or won't start on the body | Thread over-cut, or chips in the thread, or the anodize added thickness | Clean; re-chase; ease the thread after anodizing |
| Ring loosens when wet | No lock; thread too coarse for the load | Add an O-ring or nylon washer; add a lock ring |
| Seat wobbles on the blank | Bushings oversize or too thin | Re-fit; thicken the epoxy; recheck alignment while curing |
| Seat won't slide on over the hex corners | Bore smaller than 0.325″ across corners | Bore to 0.340″+ or use bushings |
| Grip glue line shows | Too much glue between the rings | Use less; sand back a little |
| Grip cracks on reaming | Reamed before cure; too fast | Wait; ream in steps |
| Voids in the finished cork | Poor rings | Fill and sand; move low-grade rings to the ends |
| Reel rattles in the seat | Channel too long or the hood too shallow | Shim with tape, or recut with a tighter channel |
| Cork dust everywhere | Dry sanding | Outdoors or with a vacuum |

## Safety

- **Lathe PPE:** safety glasses or face shield; no loose sleeves, gloves,
  or jewelry; long hair tied back; chuck key out before power on. Run the
  lathe at a sensible speed for the stock size, and stand out of the line of
  the chuck. Remove burrs and sharp edges before handling parts.
- **Threading:** cut aluminum with light passes and coolant; watch for
  stringy chips and don't clear them by hand.
- **Cork dust:** wear a dust mask (N95 or better) and use dust collection;
  work outdoors or with a shop vacuum.
- **Epoxy:** nitrile gloves and ventilation; solvents (alcohol) away from
  ignition sources; don't use epoxy past its working time.
- **Anodizing chemicals** (if home-done): acids, gloves, goggles, and
  disposal rules. **To confirm** whether I'd do that or send it out.

## Sources

I opened and read these for this page. They cover the **grip** and the
**seat sizing**; I did not find an opened source for reel-seat thread
specs or for turning a reel seat from bar stock, so those sections are my
own plan.

- [Global FlyFisher: Making Grips II](https://globalflyfisher.com/rod-building/making-grips-ii)
  ([archive](https://web.archive.org/web/2024/https://globalflyfisher.com/rod-building/making-grips-ii)):
  off-blank ring glue-up, mandrel sizing, Titebond, 60-grit to 320-grit
  turning, ring prices
- [In-Fisherman: 7 Reminders for Building Custom Cork Grips](https://www.in-fisherman.com/editorial/7-reminders-for-building-custom-cork-grips/154570)
  ([archive](https://web.archive.org/web/2024/https://www.in-fisherman.com/editorial/7-reminders-for-building-custom-cork-grips/154570)):
  waxing the mandrel, sparing glue, composite vs. standard cork, removing
  the grip
- [Mud Hole: 4 Steps to Shape Custom Cork Grips](https://mudhole.com/blogs/tips-tricks/4-steps-to-shape-custom-cork-grips)
  ([archive](https://web.archive.org/web/2024/https://mudhole.com/blogs/tips-tricks/4-steps-to-shape-custom-cork-grips)):
  spinning-mandrel shaping, reaming, bonding with epoxy
- Mud Hole product pages, for dimensions:
  [Fuji VSS Standard seat](https://mudhole.com/products/fuji-vss-standard-versatile-spinning-reel-seat)
  ([archive](https://web.archive.org/web/2024/https://mudhole.com/products/fuji-vss-standard-versatile-spinning-reel-seat)),
  [overstock cork rings](https://mudhole.com/products/overstock-cork-rings-25-id)
  ([archive](https://web.archive.org/web/2024/https://mudhole.com/products/overstock-cork-rings-25-id))

Back to the [Rod 002 build log](/docs/rodmaking/builds/002-french-broad-spinning-rod/).
