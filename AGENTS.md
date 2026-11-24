# extra-ransom (super-chainsaw)

A personal Hugo static site — build-log and knowledge base covering split-cane bamboo fly-rod making, plus woodworking, coffee roasting, and fishing notes. Live at https://www.extra-ransom.net. The project names are random generator output and carry no meaning.

## Project Structure

```
extra-ransom/
├── config.yaml               # Hugo site config (module import, menu, params, S3 deploy target)
├── go.mod / go.sum           # Hugo Modules manifest — pins the Hextra theme
├── Makefile                  # build / serve / clean targets
├── archetypes/
│   └── default.md            # front-matter template for `hugo new` (draft: true)
├── content/
│   ├── _index.md             # site landing page
│   └── docs/                 # All site content (Hextra sidebar tree)
│       ├── equipment.md
│       ├── rodmaking/        # all rod content (menu: Rodmaking)
│       │   ├── morgan-hand-mill.md          # Tom Morgan build-class notes
│       │   ├── morgan-hand-mill-manual.md   # re-written MHM machine/manual reference
│       │   ├── tapers.md, printable-rod-tools.md
│       │   ├── builds/       # per-rod build logs
│       │   └── binders/      # binder designs & notes
│       ├── woodworking/      # incl. furniture-plans/ (menu: Woodworking) — dimensioned plans with SVG drawings
│       ├── coffee-roasting/  # (menu: Coffee Roasting)
│       └── fishing/          # trip dossiers (menu: Fishing)
├── static/
│   ├── static/               # Binary assets (photos, PDFs, STLs) — served at /static/<topic>/…
│   ├── warbirds/             # Standalone page "Mustang & Company" (plain HTML/CSS/JS) — /warbirds/
│   ├── salamanders/          # Standalone page "Salamanders of Western North Carolina" — /salamanders/
│                             #   (+ methods.html: research methods & re-run workbook)
│   └── frame-calc/           # Standalone page "Picture Frame Calculator" — /frame-calc/ (js/calc.js math, js/app.js UI)
├── workers/
│   ├── couch-to-5k/          # Cloudflare Worker + D1 API for the 5K page's shared logs (wrangler; not deployed by CI)
│   ├── eink-frame/           # Cloudflare Worker + D1 API for the e-ink gift frames (weather + poem/message; wrangler, not CI)
│   └── rv-temp/              # Cloudflare Worker + D1 for the RV temperature sensor (firmware: tommyorndorff/rv-sensor; not deployed by CI)
├── firmware/
│   └── eink-frame/           # PlatformIO firmware for the frames (FireBeetle 2 ESP32-E + Waveshare 7.5″ V2; not deployed)
├── tools/
│   ├── salamanders/photos.py # iNaturalist photo fetch/review/install + credits.js sync (not deployed)
│   ├── frame-calc/calc.test.js # `node --test tools/frame-calc/` — math tests for the frame calculator (not deployed)
│   └── woodworking/          # SVG drawing generators for the furniture plans (not deployed; see Content Conventions)
└── .github/
    └── workflows/
        └── workflow.yml      # CI "Deploy": build → S3 sync + CloudFront invalidation + gh-pages
```

Each subdirectory under `content/docs/` has an `_index.md` (section landing page). Top-level menu entries are defined in `config.yaml` under `menu.main`.

## Tech Stack

- **Hugo** (extended, v0.163.3+) static site generator
- **Hextra** theme (`github.com/imfing/hextra`) loaded via **Hugo Modules** — pinned in `go.mod` (currently `v0.12.3`). No git submodule; `hugo` fetches the module from the Go module cache.
- **Goldmark** renderer with `unsafe: true` (inline HTML and `<details>` blocks are used in content)
- **GoAT** for ASCII diagrams (```goat fenced blocks → inline SVG; a Hugo core feature, theme-independent)
- Hosted on **AWS S3** (`s3://www.extra-ransom.net`) behind **CloudFront** (`E2498U24MEPPED`)
- Mirrored to **GitHub Pages** via `peaceiris/actions-gh-pages`

## Development

Requires Hugo extended and Go (Go is needed for Hugo Modules to resolve the theme).

```bash
make serve    # hugo server --buildDrafts → http://localhost:1313 (shows drafts)
make build    # hugo → public/
make clean    # remove public/ and resources/_gen/

hugo mod get  # (re)fetch the Hextra theme module if the cache is cold
```

Manual deploy (requires the `extra-ransom` AWS profile and the Homebrew `withdeploy` Hugo build):
```
AWS_PROFILE=extra-ransom hugo deploy --maxDeletes -1 --force
```

## Content Conventions

- All content lives under `content/docs/` — Hextra renders this as the sidebar navigation tree.
- Page ordering uses `weight:` in front matter; lower weight = higher in sidebar.
- `draft: true` gates unfinished pages (visible via `make serve`, hidden in CI builds).
- Content uses **plain Markdown, tables, GoAT diagrams, and raw `<details>` HTML** — no Hextra shortcodes are currently used. Prefer blockquotes over theme-specific callout shortcodes to keep pages theme-portable.
- **No `"` inside GoAT blocks** — write inch marks as `″` (U+2033). A stray `"` in a diagram's text sends `hugo --minify` into XML mode for the rest of the page (`<a .../>`, `<td/>`), so heading anchors swallow the following paragraphs.
- External links pair with a Wayback Machine archive URL for archival discipline (the `https://web.archive.org/web/2024/<url>` form redirects to the latest snapshot). Exception: shopping-list product links (retail pages with photos) go unpaired, since they're rarely archived and a dead archive link fails the external link check.
- Tapers are stored as Markdown tables within page content.
- **Furniture plans** (`content/docs/woodworking/furniture-plans/`) are dimensioned, true-scale builds. Plans copied from a maker's piece label every number **(stated)** (from the maker), **(derived)** (worked out so the stated ones close) or **(est.)** (measured off photos), and end with an "Open questions" list. Their drawings are **SVGs generated by `tools/woodworking/*_drawings.py`** into `static/static/woodworking/` (`python3 tools/woodworking/<name>_drawings.py`) — edit the constants in the script and re-run rather than hand-editing the SVGs, and embed them as `[![alt](/static/woodworking/x.svg)](/static/woodworking/x.svg)`. The scripts share one `Drawing` helper (`modern_craftsman_drawings.py`); drawings have a white background so they read in dark mode. Prefer SVGs over ASCII/GoAT for plans — GoAT is hard to read at this scale. For print-at-1:1 templates, `python3 tools/woodworking/print_tiles.py <svg> --ppi <px per inch> [--grid] [--crop x,y,w,h]` tiles an SVG into letter sheets (1″ grid option, overlap guides, scale bar) as `<name>-print.pdf` (needs `rsvg-convert`); `--ppi` is the scale constant (`s`/`S`/`K`/`P`) in the matching `*_drawings.py`.
- **3D-printed shop tools** (`content/docs/woodworking/printed-tools.md`): STLs, preview PNGs and the parametric `generate_woodworking_stls.py` live together in `static/static/woodworking-3d/` (served at `/static/woodworking-3d/…`), like the rodmaking set in `rod-tools-3d/`. Edit the parameter block and re-run (`pip install manifold3d trimesh numpy matplotlib`); the script validates each part watertight.
- **Picture Frame Calculator** (`static/frame-calc/`): inches in, member lengths (outside long point, inside at sight and rabbet), cut list, mat BOM out; prints to PDF and embeds a `FC1.…~` reload code that the page can read back from a saved PDF (pdf.js lazy-loaded from cdnjs). Math lives in `js/calc.js` (DOM-free, tested by `tools/frame-calc/calc.test.js`); geometry mirrors `tools/woodworking/picture_frame_drawings.py`. Bump the `?v=` on its css/js when they change.
- **E-ink gift frames** (`content/docs/miscellany/eink-gift-frames.md`): three parts that must stay in sync — the parametric case (`static/static/eink-frame/generate_eink_frame_stls.py` → STLs + previews; it fit-checks panel/board/battery/adapter against the frame and cover, so edit its parameters and re-run), the firmware (`firmware/eink-frame/`, `EINK_TOKEN=<token> pio run -t upload`; pins in `include/config.h`, root CAs regenerated by `tools/make_roots.sh`), and the worker (`workers/eink-frame/`, route `www.extra-ransom.net/api/eink/*`, admin page served by the worker at `/api/eink/admin`; `npm test`). The worker's JSON payload is the contract between them (documented in its README). Fonts on the frame are Latin-1 only, so the worker runs all text through `latin1Safe()`.
- Static assets (images, PDFs, STL previews) go in `static/static/<topic>/` and are referenced as `/static/<topic>/filename`.
- New pages: `hugo new docs/<section>/<name>.md` uses `archetypes/default.md` (sets `draft: true`).
- **Standalone pages** live in `static/<name>/` as self-contained `index.html` + `css/` + `js/` + `assets/` (no build step, relative paths, no Hextra). Hugo copies them verbatim and they're linked from the "Standalone pages" grid on `content/_index.md`. The grid also carries an external card for **CaneDNA** (`https://canedna.extra-ransom.net/`, the taper-explorer WASM app from the separate `canedna` repo). Because CI gives `*.css`/`*.js`/images a 1-year immutable cache, their CSS/JS references carry a `?v=YYYYMMDD` query — bump it whenever those files change. Salamander data lives in `static/salamanders/js/data.js`; photo credits in `assets/img/credits.json`, mirrored to `js/credits.js` by `tools/salamanders/photos.py credits`. **Before changing salamander content, read `static/salamanders/methods.html`** — it records the source hierarchy, deliberate naming/scope decisions, unverified items, and the recurring-checks workbook; keep it in sync when you change data or prose. **Couch to Turkey Trot** (`static/couch-to-5k/`) is a dependency-free checklist calendar with a guided interval timer, three plan levels (`js/plan.js`: beginner / intermediate / runner; dates and run/walk segments in seconds; Thanksgiving 2026 is Thu Nov 26), a per-person log (distance, time, rough running share, notes) and a progress summary page (`summary/`). A public `team/` page shows everyone as colored dots (no names; each person picks their color). Every calendar day (not just run days) has yes/no chips for strength training and sauna plus a bike chip that cycles off / indoor / outdoor (`days` table, `PUT /api/c25k/days/:date`; private, not on the team page). The log form can import a Garmin Connect TCX/GPX export (`js/import.js`, parsed in the browser, running share estimated from cadence/speed; FIT is not supported). Opened plain, it stores data in `localStorage` (`c25k-trot-2026-v2`). Opened with `?p=<token>` it talks to the Cloudflare Worker + D1 backend in `workers/couch-to-5k/` (deployed separately with wrangler, not by CI; see its README) via `js/store.js`; `admin/` creates people and their links. The dates are hard-coded to 2026. The warbirds page was built in a separate session and has no methods record; its README-level notes (photo sources, specs caveat) are in the page footer.

## CI/CD

`.github/workflows/workflow.yml` ("Deploy") triggers on push to `main` (and `workflow_dispatch`):
1. Checkout (`fetch-depth: 0`) — no submodules; Hugo Modules resolves the theme at build time.
2. Install Hugo extended `0.163.3` via `peaceiris/actions-hugo`.
3. Build with `hugo --minify`.
4. Assume AWS role via **OIDC** (`role-to-assume: …:role/extra-ransom-github-deploy`) — no long-lived keys.
5. Two-pass `aws s3 sync ./public/ …`: first pass sets a 1-year immutable cache on hashed assets (css/js/svg/img/fonts/ico); second pass sets `max-age=0, must-revalidate` on everything else (html/xml/json/…). Both use `--delete`.
6. `aws cloudfront create-invalidation … --paths "/*"`.
7. Deploy `./public` to the `gh-pages` branch via `peaceiris/actions-gh-pages` with `cname: extra-ransom.net`.

Auth: GitHub OIDC (IAM role trust), not access-key secrets. See `README.md` for the IAM policy and OIDC setup pointer.

## Known Limitations

- Hugo version is pinned in two places (CI `workflow.yml` and local Homebrew) — bump both together to stay reproducible.
- The Hextra theme is pinned via `go.mod`; run `hugo mod get -u github.com/imfing/hextra` to update it deliberately.
- The `.gitignore` is a Node.js template leftover from a prior Gatsby stack; irrelevant entries can be ignored.
