# extra-ransom

A personal static site — build-log and knowledge base covering split-cane bamboo fly-rod making, plus fishing trips, woodworking, coffee roasting, hydroponics and miscellany. Live at https://www.extra-ransom.net.

## Project Structure

```
extra-ransom/
├── astro.config.mjs          # Astro + Starlight config (site, sidebar, redirects, edit link, link validator)
├── package.json / package-lock.json
├── tsconfig.json
├── src/
│   ├── content.config.ts     # Starlight docs collection + front-matter schema
│   ├── redirects.json        # old URL -> new URL (Hugo aliases, rodmaking/fishing merge)
│   ├── styles/custom.css     # theme tweaks (palette, fonts, hero, white drawings in dark mode)
│   └── content/docs/
│       ├── index.mdx         # home page (splash)
│       └── docs/             # all content, served at /docs/...
│           ├── equipment.md  # draft
│           ├── rods-and-fishing/
│           │   ├── making/   # rod making: tapers, Morgan Hand Mill, printable tools, binders/, builds/
│           │   └── trips/    # fishing trip dossiers
│           ├── woodworking/  # incl. furniture-plans/ (dimensioned plans with SVG drawings)
│           ├── coffee-roasting/
│           ├── hydroponics/
│           └── miscellany/
├── public/                   # copied verbatim to the site root (Astro `public/`)
│   ├── static/               # binary assets (photos, PDFs, STLs, SVG drawings) -> /static/<topic>/...
│   ├── goat/                 # static SVG diagrams -> /goat/...
│   ├── warbirds/             # standalone page "Mustang & Company" (plain HTML/CSS/JS)
│   ├── salamanders/          # standalone page "Salamanders of Western North Carolina" (+ methods.html)
│   ├── frame-calc/           # standalone "Picture Frame Calculator" (js/calc.js math, js/app.js UI)
│   ├── couch-to-5k/          # standalone "Couch to Turkey Trot" checklist calendar
│   └── norway/               # standalone Norway trip pages
├── workers/
│   ├── couch-to-5k/          # Cloudflare Worker + D1 API for the 5K page's shared logs (wrangler; not deployed by CI)
│   ├── eink-frame/           # Cloudflare Worker + D1 API for the e-ink gift frames (wrangler, not CI)
│   └── rv-temp/              # Cloudflare Worker + D1 for the RV temperature sensor (firmware: tommyorndorff/rv-sensor; not deployed by CI)
├── firmware/
│   └── eink-frame/           # PlatformIO firmware for the frames (FireBeetle 2 ESP32-E + Waveshare 7.5″ V2; not deployed)
├── tools/                    # generators and tests, not deployed
│   ├── salamanders/photos.py # iNaturalist photo fetch/review/install + credits.js sync
│   ├── frame-calc/calc.test.js # `node --test tools/frame-calc/calc.test.js` — math tests for the frame calculator
│   └── woodworking/          # SVG drawing generators for the furniture plans (see Content Conventions)
├── docs/aws-oidc-setup.md    # GitHub OIDC role + deploy policy setup
└── .github/workflows/        # workflow.yml (Deploy), pr-checks.yml, link-check.yml
```

## Tech Stack

- **Astro 7** static site generator with **Starlight** (docs theme), Markdown/MDX content collection. No Hugo, no Go.
- **Pagefind** search (built in by Starlight; indexed at build time into `dist/pagefind/`).
- **starlight-links-validator**: `npm run build` fails on a broken internal link. Standalone pages and assets (`/warbirds/**`, `/salamanders/**`, `/couch-to-5k/**`, `/norway/**`, `/frame-calc/**`, `/static/**`, `/goat/**`) are excluded because they are not Starlight pages.
- **Static SVG diagrams** under `public/goat/` (originally GoAT ASCII art, rendered once).
- Hosted on **AWS S3** (`s3://www.extra-ransom.net`) behind **CloudFront** (`E2498U24MEPPED`); mirrored to **GitHub Pages** via `peaceiris/actions-gh-pages`.
- Node 22 (CI uses Node 22; `package-lock.json` is the source of truth for dependencies).

## Development

```bash
npm ci            # install (use `npm install` when changing dependencies)
npm run dev       # dev server -> http://localhost:4321
npm run build     # production build -> dist/ (Pagefind index + link validation)
npm run preview   # serve dist/ locally
```

`dist/`, `.astro/` and `node_modules/` are git-ignored; `public/` is source and is tracked.

There is no manual deploy path any more (the old `hugo deploy` flow is gone): deploys happen from CI on push to `main`. To deploy by hand, build and run the same two `aws s3 sync` passes shown in `.github/workflows/workflow.yml` with the `extra-ransom` AWS profile.

## Content Conventions

- All pages live under `src/content/docs/` (Starlight content collection). Pages under `src/content/docs/docs/<section>/` are served at `/docs/<section>/<page>/`; the home page is `src/content/docs/index.mdx` (splash template, hand-written HTML). A directory's landing page is its `index.md`.
- Front matter: `title`, optional `date`, `draft: true`, and `sidebar: { order: N }` (lower = higher in the sidebar; this replaced Hugo's `weight:`). A few pages still carry a legacy `weight:` key — it is accepted by `src/content.config.ts` but does nothing.
- The sidebar is defined in `astro.config.mjs`: each section lists its own pages (sorted by `sidebar.order`, then filename; drafts skipped) and its subdirectories become labelled, collapsed groups. A new page in an existing directory shows up automatically; a new *subdirectory* needs a `sub(...)` entry there.
- `draft: true` pages are left out of the build and the sidebar (`equipment.md` is the current draft). `npm run dev` also skips them.
- Content is **plain Markdown (or MDX for the home page), tables, static SVG diagrams, and raw `<details>` HTML**. No Starlight components are used in the docs pages; prefer blockquotes over callouts to keep pages portable.
- **Diagrams are static SVGs committed under `public/goat/`** and embedded as `![diagram](/goat/<name>.svg)`. They were rendered once from GoAT ASCII art when the site moved off Hugo; there is no converter any more, so editing a diagram means editing or regenerating the SVG. To make a new one from ASCII art: `go install github.com/blampe/goat/cmd/goat@latest`, then `goat diagram.txt > public/goat/<name>.svg` (inch marks as `″`, not `"`), and embed it as an image.
- Pages live at the same URLs as under the old Hugo site, except rodmaking and fishing, which merged into `/docs/rods-and-fishing/{making,trips}/`. Old URLs and Hugo aliases redirect via `src/redirects.json` (Astro writes meta-refresh pages); add a line there whenever you move or rename a published page.
- External links pair with a Wayback Machine archive URL for archival discipline (the `https://web.archive.org/web/2024/<url>` form redirects to the latest snapshot). Exception: shopping-list product links (retail pages with photos) go unpaired, since they're rarely archived and a dead archive link fails the external link check.
- Tapers are stored as Markdown tables within page content.
- **Furniture plans** (`src/content/docs/docs/woodworking/furniture-plans/`) are dimensioned, true-scale builds. Plans copied from a maker's piece label every number **(stated)** (from the maker), **(derived)** (worked out so the stated ones close) or **(est.)** (measured off photos), and end with an "Open questions" list. Their drawings are **SVGs generated by `tools/woodworking/*_drawings.py`** into `public/static/woodworking/` (`python3 tools/woodworking/<name>_drawings.py`) — edit the constants in the script and re-run rather than hand-editing the SVGs, and embed them as `[![alt](/static/woodworking/x.svg)](/static/woodworking/x.svg)`. The scripts share one `Drawing` helper (`modern_craftsman_drawings.py`); drawings have a white background so they read in dark mode. Prefer SVGs over ASCII diagrams for plans — those are hard to read at this scale. For print-at-1:1 templates, `python3 tools/woodworking/print_tiles.py <svg> --ppi <px per inch> [--grid] [--crop x,y,w,h]` tiles an SVG into letter sheets (1″ grid option, overlap guides, scale bar) as `<name>-print.pdf` (needs `rsvg-convert`); `--ppi` is the scale constant (`s`/`S`/`K`/`P`) in the matching `*_drawings.py`.
- **3D-printed shop tools** (`src/content/docs/docs/woodworking/printed-tools.md`): STLs, preview PNGs and the parametric `generate_woodworking_stls.py` live together in `public/static/woodworking-3d/` (served at `/static/woodworking-3d/…`), like the rodmaking set in `rod-tools-3d/`. Edit the parameter block and re-run (`pip install manifold3d trimesh numpy matplotlib`); the script validates each part watertight.
- **Picture Frame Calculator** (`public/frame-calc/`): inches in, member lengths (outside long point, inside at sight and rabbet), cut list, mat BOM out; prints to PDF and embeds a `FC1.…~` reload code that the page can read back from a saved PDF (pdf.js lazy-loaded from cdnjs). Math lives in `js/calc.js` (DOM-free, tested by `tools/frame-calc/calc.test.js`); geometry mirrors `tools/woodworking/picture_frame_drawings.py`. Bump the `?v=` on its css/js when they change.
- **E-ink gift frames** (`src/content/docs/docs/miscellany/eink-gift-frames.md`): three parts that must stay in sync — the parametric case (`public/static/eink-frame/generate_eink_frame_stls.py` → STLs + previews; it fit-checks panel/board/battery/adapter against the frame and cover, so edit its parameters and re-run), the firmware (`firmware/eink-frame/`, `EINK_TOKEN=<token> pio run -t upload`; pins in `include/config.h`, root CAs regenerated by `tools/make_roots.sh`), and the worker (`workers/eink-frame/`, route `www.extra-ransom.net/api/eink/*`, admin page served by the worker at `/api/eink/admin`; `npm test`). The worker's JSON payload is the contract between them (documented in its README). Fonts on the frame are Latin-1 only, so the worker runs all text through `latin1Safe()`.
- Static assets (images, PDFs, STL previews, regenerated SVG drawings) go in `public/static/<topic>/` and are referenced as `/static/<topic>/filename` (Astro serves `public/` at the site root). The same long cache applies to SVGs (including regenerated furniture drawings and `public/goat/`), so a changed SVG at an unchanged name can look stale in browsers/CloudFront until its cache expires — rename the file or invalidate when it matters.
- New pages: create `src/content/docs/docs/<section>/<name>.md` with `title:` front matter (add `draft: true` while unfinished).
- **Standalone pages** live in `public/<name>/` as self-contained `index.html` + `css/` + `js/` + `assets/` (no build step, relative paths, no Starlight). Astro copies `public/` verbatim and they're linked from the "Standalone pages" grid on `src/content/docs/index.mdx`. The grid also carries an external card for **CaneDNA** (`https://canedna.extra-ransom.net/`, the taper-explorer WASM app from the separate `canedna` repo). Because CI gives `*.css`/`*.js`/`*.svg`/images a 1-year immutable cache, their CSS/JS references carry a `?v=YYYYMMDD` query — bump it whenever those files change. Salamander data lives in `public/salamanders/js/data.js`; photo credits in `assets/img/credits.json`, mirrored to `js/credits.js` by `tools/salamanders/photos.py credits`. **Before changing salamander content, read `public/salamanders/methods.html`** — it records the source hierarchy, deliberate naming/scope decisions, unverified items, and the recurring-checks workbook; keep it in sync when you change data or prose. **Couch to Turkey Trot** (`public/couch-to-5k/`) is a dependency-free checklist calendar with a guided interval timer, three plan levels (`js/plan.js`: beginner / intermediate / runner; dates and run/walk segments in seconds; Thanksgiving 2026 is Thu Nov 26), a per-person log (distance, time, rough running share, notes) and a progress summary page (`summary/`). A public `team/` page shows everyone as colored dots (no names; each person picks their color). Every calendar day (not just run days) has yes/no chips for strength training and sauna plus a bike chip that cycles off / indoor / outdoor (`days` table, `PUT /api/c25k/days/:date`; private, not on the team page). The log form can import a Garmin Connect TCX/GPX export (`js/import.js`, parsed in the browser, running share estimated from cadence/speed; FIT is not supported). Opened plain, it stores data in `localStorage` (`c25k-trot-2026-v2`). Opened with `?p=<token>` it talks to the Cloudflare Worker + D1 backend in `workers/couch-to-5k/` (deployed separately with wrangler, not by CI; see its README) via `js/store.js`; `admin/` creates people and their links. The dates are hard-coded to 2026. The warbirds page was built in a separate session and has no methods record; its README-level notes (photo sources, specs caveat) are in the page footer.

## CI/CD

`.github/workflows/workflow.yml` ("Deploy") triggers on push to `main` (and `workflow_dispatch`):
1. Checkout (`fetch-depth: 0`).
2. `actions/setup-node@v4` (Node 22, npm cache), `npm ci`.
3. `npm run build` -> `dist/` (fails on broken internal links).
4. Assume AWS role via **OIDC** (`role-to-assume: …:role/extra-ransom-github-deploy`) — no long-lived keys.
5. Two-pass `aws s3 sync ./dist/ …` (both `--delete`): the first pass sets a 1-year immutable cache on css/js/svg/img/fonts/ico (this covers Astro's hashed `/_astro/` files) but **excludes `pagefind/*`**; the second pass sets `max-age=0, must-revalidate` on everything else and explicitly re-includes `pagefind/*`. Pagefind's files have fixed names (`pagefind.js`, `pagefind-ui.js`, entry json) and change on every build, so they must not be cached as immutable.
6. `aws cloudfront create-invalidation … --paths "/*"`.
7. Deploy `./dist` to the `gh-pages` branch via `peaceiris/actions-gh-pages` with `cname: extra-ransom.net`.

`pr-checks.yml` (build + lychee offline internal-link check on `dist/`) and `link-check.yml` (lychee external link check, config in `.lychee.toml`) also build with Node 22 and check `./dist`.

Auth: GitHub OIDC (IAM role trust), not access-key secrets. See `README.md` and `docs/aws-oidc-setup.md`.

## Known Limitations

- Action versions are tag-pinned (`@v4`), not SHA-pinned.
- Diagrams are static SVGs; changing one means editing/regenerating the SVG by hand.
- Link validation covers Starlight pages only; links inside standalone pages are covered only by the lychee jobs.
- Markdown links into `/static/...` assets are not validated (excluded), so a typo'd asset path is only caught by lychee.
- The edit-this-page link on each docs page points at `https://github.com/tommyorndorff/extra-ransom/edit/main/src/content/docs/…`.
- `.gitignore` still contains Node/Gatsby template leftovers; irrelevant entries can be ignored.
- Cloudflare Workers (`workers/`) and firmware are deployed manually and are not part of CI.
