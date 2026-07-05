---
title: "Logging Roasts to This Site"
weight: 20
---

How to export a roast from Artisan and add it as a page on this site.

## Roast Phase Buttons

Artisan's toolbar has one button per roast phase — press each the instant it happens. Use the trier (the little sampling scoop on the roaster) to judge color for Dry End, and listen for the cracks:

| Button | Press it when... |
|---|---|
| **CHARGE** | Beans go into the roaster. This is the zero point everything else is measured from — no CHARGE, no ∆BT curve. |
| **DRY END** | The beans finish drying and start browning (Maillard) — pull a sample with the trier and watch the color shift from green to tan/yellow. |
| **FC START** | First crack audibly begins — a popcorn-like popping. |
| **FC END** | First crack's popping tapers off. |
| **SC START** | Second crack begins, if roasting past first crack — a faster, higher-pitched crackle than first crack. |
| **SC END** | Second crack's crackling tapers off. |
| **DROP** | Beans come out of the roaster into the cooling tray. |

**Turning Point isn't a button.** Artisan auto-detects it as the lowest bean-temp reading shortly after Charge — the moment the cold beans stop dragging the temperature down and it starts climbing. That makes it the one phase mark that can go wrong even when you press every button correctly: if the probe glitches right after Charge, like on [the first roast logged here](/docs/coffee-roasting/2026-07-05-honduras-finca-el-conejo-catuai-organic/), the auto-detected TP is meaningless even though every button-marked event on the same roast is fine.

## What to Capture Per Roast

Enter bean and weight data straight into Artisan's own **Roast Properties** dialog (`Roast` menu, or click the roast title above the graph) as you go — it's saved into the `.alog` file automatically, so there's nothing to transcribe later:

- **Roast tab**: `Beans` (origin, variety, processing — e.g. "Ethiopia Yirgacheffe, washed"), `Green Weight`, `Roasted Weight` (Artisan computes weight loss % from these two)
- **Title**: batch identifier, shown on the graph itself
- **Notes tab**: roasting notes during the session, cupping notes once it's rested

Charge, turning point, first crack, and drop don't need writing down either — mark each one live with Artisan's phase buttons/hotkeys as it happens, and the exact time and temp land on the graph and in the saved profile on their own.

---

## Exporting from Artisan

### Roast Curve Image

After the roast completes (or during):

1. **File > Save Graph** — saves the roast curve as a `.png` (also offers PDF and social-media-sized exports).

For a clean export, use **View > Full Screen** first so the graph fills the window before saving.

### Roast Data (Artisan `.alog`)

1. **File > Save As** — saves the full roast as an Artisan `.alog` file (JSON format), including every temperature sample, event marker, and the Roast Properties entered above.

Keep this file alongside the page as a data archive even if you don't embed it in the site — it's the only copy of the raw curve data, and it's what [ArtisanViewer](https://artisan-scope.org/) or a future Artisan version would need to re-open the roast.

**Optional:** Artisan's [Autosave](https://artisan-scope.org/docs/autosave/) feature (`Config > Autosave`) can write both the `.alog` and a rendered image/PDF automatically at the end of every roast, using a filename template built from the roast date and bean name — worth setting up once instead of doing the File > Save Graph / File > Save As dance by hand every time.

---

## Where to Store Files

```
static/static/coffee-roasting/
└── YYYY-MM-DD-bean-name/
    ├── roast-curve.png     ← exported graph image
    └── roast.alog          ← Artisan data file (optional, for archiving)
```

Example:
```
static/static/coffee-roasting/2025-01-15-ethiopia-yirgacheffe/roast-curve.png
```

The file will be served at:
```
/static/coffee-roasting/2025-01-15-ethiopia-yirgacheffe/roast-curve.png
```

---

## Creating a Roast Page

Each roast gets its own Markdown file under `content/docs/coffee-roasting/`.

```bash
hugo new docs/coffee-roasting/2025-01-15-ethiopia-yirgacheffe.md
```

### Page Template

```markdown
---
title: "2025-01-15 Ethiopia Yirgacheffe"
date: 2025-01-15
weight: 200
---

**Bean**: Ethiopia Yirgacheffe, washed
**Source**: [Roaster name]
**Green weight**: 250g | **Roast out**: 210g (16% loss)

## Roast

| | Temp | Time |
|---|---|---|
| Charge | 195°C | 0:00 |
| Turning point | 92°C | 1:45 |
| First crack | 196°C | 9:30 |
| Drop | 207°C | 11:00 |

![Roast curve](/static/coffee-roasting/2025-01-15-ethiopia-yirgacheffe/roast-curve.png)

## Notes

Notes on the roast — airflow adjustments, gas changes, anything that
went well or needs adjustment next time.

## Cup

Tasting notes after resting 5–7 days.
```

---

## Keeping Pages Ordered

Use `weight` in front matter to control sidebar order. Lower numbers appear first. A convention that works well:

- Section `_index.md`: `weight: 100`
- Individual roast pages: use the date as a weight, e.g. `weight: 20250115` for 2025-01-15

This keeps roasts sorted chronologically from oldest (top) to newest (bottom). Reverse it by assigning descending weights.

---

## Publishing

Add the new page and static files, then push to `main` — CI deploys automatically.

```bash
git add content/docs/coffee-roasting/ static/static/coffee-roasting/
git commit -m "roast: 2025-01-15 Ethiopia Yirgacheffe"
git push
```
