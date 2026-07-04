# EPCC — Explore: `extra-ransom`

> Archaeological report by **CodeDigger**. Exploration only — no source files were modified.
> Repo: `/Users/torndorff/Projects/git/extra-ransom` · Branch: `main` · Date: 2026-07-04

---

## 1. What This Project IS

**`extra-ransom` (aka "super-chainsaw") is a personal, static documentation website about building split-cane bamboo fly-fishing rods.**

- **Purpose**: A public knowledge base / build-log where the author documents the craft of bamboo rod making — equipment, tools, tapers, binders (the machines that wrap glued strips), class notes, and individual rod projects. Much of it is deliberately archived material (the author repeatedly preserves source links via the Wayback Machine because "my brain isn't the lint catch that it used to be").
- **Audience**: Fellow amateur/hobbyist bamboo rodmakers, and the author's own future reference.
- **Domain**: Traditional woodworking / bamboo (split-cane) fly rod construction. Recurring vocabulary: *culms, power fibers, tapers, ferrules, binders (Garrison/Smithwick), Morgan Hand Mill (MHM), heat treating, glue-up, stations*.
- **Name origin (documented in README)**: "extra-ransom" and "super-chainsaw" are random project-name-generator outputs and **mean nothing** — do not read intent into them.
- **Live site**: https://www.extra-ransom.net

---

## 2. Technology Stack

| Layer | Technology | Evidence |
|---|---|---|
| Static Site Generator | **Hugo** | `config.yaml`, `.hugo_build.lock`, `archetypes/`, `resources/_gen`, CI `peaceiris/actions-hugo` |
| Theme | **hugo-book** (`alex-shpak/hugo-book`) | `theme: hugo-book` in config; git submodule in `.gitmodules` |
| Content format | **Markdown** with YAML front matter + Goldmark (unsafe HTML enabled) | `markup.goldmark.renderer.unsafe: true` |
| Diagrams | **goat** ASCII diagram fences (```` ```goat ````) | `morgan-hand-mill.md` |
| Hosting | **AWS S3** static bucket (`www.extra-ransom.net`, us-east-1) | `config.yaml` deployment target, README |
| CDN | **AWS CloudFront** distribution `E2498U24MEPPED` | config + CI invalidation |
| CI/CD | **GitHub Actions** (deploy on push to `main`) | `.github/workflows/workflow.yml` |
| Secondary deploy target | **GitHub Pages** (`gh-pages` branch, `peaceiris/actions-gh-pages`) | CI workflow |

**Notable**: The theme is a **git submodule**, currently NOT checked out in the local working copy (`themes/` is empty). CI fetches it via `actions/checkout` with `submodules: true`. Anyone cloning locally must run `git submodule update --init` before `hugo` will build.

---

## 3. Directory Structure

```
extra-ransom/
├── config.yaml                 # Hugo site config (single top-level config)
├── README.md                   # Purpose + deploy notes
├── .hugo_build.lock            # Hugo build lock artifact
├── .gitmodules                 # theme submodule → hugo-book
├── .gitignore                  # Node-flavored ignore (public/, node_modules) — legacy Gatsby leftover
├── .github/workflows/
│   └── workflow.yml            # "Deploy Blog" — build + S3 sync + CloudFront invalidation
├── archetypes/
│   └── default.md              # Front-matter template for `hugo new`
├── content/                    # ALL site content lives here
│   └── docs/                   # hugo-book's primary section (left-nav docs tree)
│       ├── equipment.md
│       ├── morgan-hand-mill.md
│       ├── garrison-binder.md
│       ├── new-smithwick-binder.md
│       ├── rod-binder-notes.md
│       ├── rod-tapers.md
│       └── projects/           # Menu section "projects"
│           ├── _index.md       # (empty — section landing placeholder)
│           ├── 001-sir-d-taper.md
│           └── chopsticks.md
├── resources/_gen/assets/scss/ # Hugo-cached compiled book.scss (generated artifact)
├── static/
│   └── static/                 # NOTE: doubly-nested — served at /static/...
│       ├── rod-binder/         # GIF/PNG/PDF binder diagrams
│       └── new-smithwick-rod-binder/  # Groth binder plans (jpg/png/pdf)
└── themes/                     # (submodule mount point; empty locally)
```

### Directory purposes
- **`content/docs/`** — The knowledge base. `docs` is hugo-book's convention for the documented, left-sidebar-navigable section.
- **`content/docs/projects/`** — A sub-section for per-rod build logs, surfaced as a top menu item via `config.yaml` `menu.main`.
- **`static/static/`** — Raw binary assets (diagrams, PDFs, photos). The double `static/static/` nesting is intentional/quirky: files resolve to URLs like `/static/rod-binder/cradle.gif`, and content references them exactly that way.
- **`resources/_gen/`** — Hugo's generated resource cache (compiled SCSS). Build artifact, not authored.

---

## 4. Content Structure

### Content types
There is effectively **one content type** — a hugo-book doc page — used in two roles:
1. **Reference/how-to pages** (`equipment`, `morgan-hand-mill`, binder pages, `rod-tapers`).
2. **Project build logs** (`content/docs/projects/*`), which attach to the `projects` menu parent.

### Taxonomies
- **No custom Hugo taxonomies** (no tags/categories) are defined. Organization is purely by **menu + weight ordering**, which is idiomatic for hugo-book.

### Organization mechanics
- **Menu**: `config.yaml` defines `menu.main` with a `projects` identifier; project pages opt in via front matter `menu.main.parent: projects`.
- **Ordering**: `weight` front matter controls sidebar order (e.g., `rod-tapers`=1, `morgan-hand-mill`=1, binders=50–55, project 001=100, chopsticks=400).
- **`sectionPagesMenu: main`** — Hugo auto-adds section pages to the main menu.
- **External menu link**: an `after` menu entry points to the GitHub repo.

---

## 5. Recurring Patterns & Conventions

1. **YAML front matter with commented-out hugo-book toggles** — nearly every page carries the same commented template block (`# bookToc:`, `# bookHidden:`, `# bookCollapseSection:`, etc.), selectively uncommented. This is a consistent copy-paste convention across content.
2. **`draft: true` gating** — unfinished pages (`equipment.md`, and the archetype default) are marked draft so they don't publish. `hugo` excludes drafts by default.
3. **Archival discipline** — external sources are almost always paired with a **Wayback Machine** link, and the author explicitly states a "preference toward Internet Archive." Content copied from other sites (e.g., the Garrison binder article) is attributed with original URL + archive URL.
4. **Asset referencing** — images use absolute `/static/...` paths and inline Markdown image syntax, placed inline after the relevant paragraph.
5. **Data-as-tables** — rod tapers are captured as detailed Markdown tables (station-by-station dimensions: Rod Dim, Half Dim, oversize allowances, MHM setting).
6. **`goat` ASCII diagrams** for hand-drawn-style layout (node staggering).
7. **`<details>/<summary>` collapsible HTML** embedded in Markdown (enabled by `unsafe: true` Goldmark), used to hide long "ramble" passages.
8. **Footnotes** (`[^1]`) used for asides and references.

---

## 6. Notable Files

- **`config.yaml`** — Single source of site config. Key items: `baseURL`, `theme: hugo-book`, Goldmark `unsafe: true`, TOC `startLevel: 1`, `menu` definitions, `params.BookTheme: auto` + `BookRepo`, and a Hugo **`deployment`** block (S3 target `s3-extra-ransom`, CloudFront ID, gzip/cache-control matchers by file extension). Enables `hugo deploy`.
- **`archetypes/default.md`** — Template for `hugo new`: title (title-cased from filename), date, `draft: true`.
- **`content/docs/projects/_index.md`** — **Empty (0 bytes of body)**; exists only to establish the section. A likely low-effort improvement target.
- **`README.md`** — Documents name origin, the build-vs-infra boundary ("It doesnt build the infra"), the deploy chain, and the manual deploy command: `AWS_PROFILE=extra-ransom hugo deploy --maxDeletes -1 --force`.
- **`.gitignore`** — A **Node.js/Gatsby-oriented** ignore file (node_modules, Gatsby cache, `public/`). This is largely vestigial — the repo is Hugo, not Node — a fossil from a prior/templated setup (corroborated by the large commented-out Gatsby block in the CI workflow).

---

## 7. Deployment / CI-CD

**Trigger**: push to `main` (workflow name: "Deploy Blog"), 10-minute timeout, `ubuntu-latest`.

**Pipeline steps** (`.github/workflows/workflow.yml`):
1. Checkout with `submodules: true` (fetches hugo-book) and `fetch-depth: 0` (full history for `.GitInfo`/`.Lastmod`).
2. Setup Hugo (`peaceiris/actions-hugo@v2`, `hugo-version: latest`).
3. `rm -rf public` (clean).
4. `hugo --theme=hugo-book` (build to `public/`).
5. Write `public/CNAME` = `extra-ransom.net` (for GitHub Pages custom domain).
6. Deploy to **GitHub Pages** `gh-pages` branch (`peaceiris/actions-gh-pages@v3`).
7. Configure AWS creds (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` secrets, us-east-1).
8. `aws s3 sync ./public/ s3://www.extra-ransom.net/ --delete`.
9. `aws cloudfront create-invalidation --distribution-id E2498U24MEPPED --paths "/"`.

**Deploy topology** (from README): `GitHub repo → S3 (www.extra-ransom.net) → CloudFront (E2498U24MEPPED)`.

**Two live sinks**: the site publishes to BOTH GitHub Pages (gh-pages) AND AWS S3+CloudFront in the same run. S3/CloudFront is the canonical target per README; the GH Pages step appears to be a retained secondary/legacy path.

**Infra scope**: This repo only builds/deploys *content*. It explicitly does **not** provision the S3 bucket, CloudFront distribution, or DNS.

---

## Risk / Debt Assessment (archaeologist's notes)

| Item | Severity | Observation |
|---|---|---|
| CloudFront invalidation `--paths "/"` | Medium | Invalidates only root, not `/*`. Updated deep pages may serve stale content from CDN cache until TTL expiry. |
| Redundant deploy targets | Low–Med | Publishing to both gh-pages and S3 doubles work and can cause confusion about the source of truth. |
| Vestigial Node/Gatsby config | Low | `.gitignore` and large commented CI block are dead weight from a prior stack — misleading to newcomers. |
| Theme pinned to `@HEAD` submodule + Hugo `latest` | Low–Med | Unpinned theme + `hugo-version: latest` means an upstream change can break a build with no code change here. No version pinning = non-reproducible builds. |
| Deprecated GitHub Actions | Low | `actions/checkout@v2`, `configure-aws-credentials@v1`, long-term AWS access keys (vs OIDC). Aging, non-critical. |
| Empty `projects/_index.md` | Low | Section landing page has no intro content. |
| Doubly-nested `static/static/` | Cosmetic | Works but is unusual; easy to trip over when adding assets. |
| Draft pages (`equipment.md`) | Info | Intentionally unpublished; not a defect. |

**Nothing was modified during this exploration.**
