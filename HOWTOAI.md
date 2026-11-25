# How to Use AI Tools with This Repo

This is an Astro + Starlight static content site. AI assistants are most useful for editing Markdown content, maintaining consistency, and working with the Astro configuration.

## Quick Start

```bash
npm ci            # install
npm run dev       # local dev server (http://localhost:4321)
npm run build     # build to dist/ (also validates internal links)
```

## What AI Can Help With

**Content editing**
- Drafting or refining pages under `src/content/docs/docs/`
- Converting taper data into Markdown tables
- Improving clarity of build-log prose

**Astro config**
- `astro.config.mjs` controls the sidebar, redirects, edit link and link validator
- Front matter fields: `title`, `date`, `draft`, `sidebar.order`

**CI/CD**
- Workflows are in `.github/workflows/` (`workflow.yml` deploys; AWS access is via OIDC)

## What to Avoid

- Do not commit `dist/`, `.astro/` or `node_modules/` — they are build output and gitignored.
- `public/` is source (static assets and standalone pages), not build output; do not ignore or delete it.
- Do not hand-edit generated SVG drawings in `public/static/woodworking/`; edit the generator in `tools/woodworking/` and re-run it.

## Project Context

See `AGENTS.md` for full architecture, conventions, and known limitations.
