# extra-ransom (super-chainsaw)

A personal Hugo static site — build-log and knowledge base for making split-cane bamboo fly-fishing rods. Live at https://www.extra-ransom.net. The project names are random generator output and carry no meaning.

## Project Structure

```
extra-ransom/
├── config.yaml               # Hugo site config (theme, baseURL, S3 deploy target)
├── Makefile                  # build / serve / clean targets
├── content/
│   └── docs/                 # All site content (hugo-book sidebar tree)
│       ├── equipment.md
│       ├── garrison-binder.md
│       ├── morgan-hand-mill.md
│       ├── new-smithwick-binder.md
│       ├── rod-binder-notes.md
│       ├── rod-tapers.md
│       └── projects/         # Per-rod build logs
│           ├── _index.md
│           ├── 001-sir-d-taper.md
│           └── chopsticks.md
├── archetypes/
│   └── default.md            # Hugo front-matter template for new pages
├── static/
│   └── static/               # Binary assets (photos, PDFs, diagrams) — served at /static/…
│       ├── new-smithwick-rod-binder/
│       └── rod-binder/
├── themes/                   # git submodule: alex-shpak/hugo-book
└── .github/
    └── workflows/
        └── workflow.yml      # CI: build → gh-pages + S3 sync + CloudFront invalidation
```

## Tech Stack

- **Hugo** static site generator + **hugo-book** theme (git submodule — fetched by CI, not checked in)
- **Goldmark** renderer with `unsafe: true` (inline HTML and `<details>` blocks are used in content)
- **GoAT** for ASCII diagrams
- Hosted on **AWS S3** (`s3://www.extra-ransom.net`) behind **CloudFront** (`E2498U24MEPPED`)
- Mirrored to **GitHub Pages** via `peaceiris/actions-gh-pages`

## Development

```bash
make serve    # local dev server at http://localhost:1313 — shows draft pages
make build    # build to public/ (mirrors CI)
make clean    # remove public/ and resources/_gen/
```

Manual deploy (requires `extra-ransom` AWS profile):
```
AWS_PROFILE=extra-ransom hugo deploy --maxDeletes -1 --force
```

## Content Conventions

- All content lives under `content/docs/` — hugo-book renders this as the sidebar navigation tree.
- Page ordering uses `weight:` in front matter; lower weight = higher in sidebar.
- `draft: true` gates unfinished pages.
- External links pair with Wayback Machine archive URLs for archival discipline.
- Tapers are stored as Markdown tables within page content.
- Static assets (images, PDFs) go in `static/static/<topic>/` and are referenced as `/static/<topic>/filename`.
- The `projects/` section is wired to the `main` menu via `config.yaml`; each rod build is its own page there.

## CI/CD

`.github/workflows/workflow.yml` ("Deploy Blog") triggers on push to `main`:
1. Checkout with submodules (fetches hugo-book theme)
2. Build with `hugo --theme=hugo-book`
3. Write `public/CNAME` (`extra-ransom.net`)
4. Push `public/` to `gh-pages` branch
5. `aws s3 sync ./public/ s3://www.extra-ransom.net/ --delete`
6. `aws cloudfront create-invalidation --distribution-id E2498U24MEPPED --paths "/"`

Secrets required: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`.

## Known Limitations

- CloudFront invalidation targets `"/"` only — deep-path pages can serve stale content after a deploy.
- Hugo version is pinned to `latest` in CI — builds are not fully reproducible.
- Theme is an unpinned submodule HEAD for the same reason.
- The `.gitignore` is a Node.js template leftover from a prior Gatsby stack; irrelevant entries can be ignored.
