---
title: "Logging Roasts to This Site"
weight: 20
---

How to export a roast from Artisan and add it as a page on this site.

## What to Capture Per Roast

At minimum, record:

- Date and batch number
- Bean origin, variety, and processing (e.g. Ethiopia Yirgacheffe, washed)
- Green weight (grams) and roast weight out (for calculating roast loss %)
- Charge temp, first crack time and temp, drop time and temp
- Artisan roast curve (exported as image)
- Notes on the roast and cup result

---

## Exporting from Artisan

### Roast Curve Image

After the roast completes (or during):

1. **File > Save Graph** — saves the roast curve as a `.png`.
2. Alternatively: **File > Print** and print to PDF, then screenshot the curve.

For a clean export, use **View > Full Screen** first so the graph fills the window before saving.

### Roast Data (Artisan JSON)

1. **File > Save** — saves the full roast as an Artisan `.alog` file (JSON format).

This file contains every temperature sample, event marker, and setting from the roast. Keep it alongside the page as a data archive even if you don't embed it in the site.

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
static/static/coffee-roasting/2026-07-04-ethiopia-yirgacheffe/roast-curve.png
```

The file will be served at:
```
/static/coffee-roasting/2026-07-04-ethiopia-yirgacheffe/roast-curve.png
```

---

## Creating a Roast Page

Each roast gets its own Markdown file under `content/docs/coffee-roasting/`.

```bash
hugo new docs/coffee-roasting/2026-07-04-ethiopia-yirgacheffe.md
```

### Page Template

```markdown
---
title: "2026-07-04 Ethiopia Yirgacheffe"
date: 2026-07-04
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

![Roast curve](/static/coffee-roasting/2026-07-04-ethiopia-yirgacheffe/roast-curve.png)

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
- Individual roast pages: use the date as a weight, e.g. `weight: 20260704` for 2026-07-04

This keeps roasts sorted chronologically from oldest (top) to newest (bottom). Reverse it by assigning descending weights.

---

## Publishing

Add the new page and static files, then push to `main` — CI deploys automatically.

```bash
git add content/docs/coffee-roasting/ static/static/coffee-roasting/
git commit -m "roast: 2026-07-04 Ethiopia Yirgacheffe"
git push
```
