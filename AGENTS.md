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
│       ├── morgan-hand-mill.md          # Tom Morgan build-class notes
│       ├── morgan-hand-mill-manual.md   # re-written MHM machine/manual reference
│       ├── rod-tapers.md
│       ├── rod-builds/       # per-rod build logs (menu: Rod Builds)
│       ├── rod-binders/      # binder designs & notes
│       ├── woodworking/      # incl. furniture-plans/ (menu: Woodworking)
│       ├── coffee-roasting/  # (menu: Coffee Roasting)
│       └── fishing/          # trip dossiers (menu: Fishing)
├── static/
│   └── static/               # Binary assets (photos, PDFs, STLs) — served at /static/<topic>/…
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
- External links pair with a Wayback Machine archive URL for archival discipline (the `https://web.archive.org/web/2024/<url>` form redirects to the latest snapshot).
- Tapers are stored as Markdown tables within page content.
- Static assets (images, PDFs, STL previews) go in `static/static/<topic>/` and are referenced as `/static/<topic>/filename`.
- New pages: `hugo new docs/<section>/<name>.md` uses `archetypes/default.md` (sets `draft: true`).

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
