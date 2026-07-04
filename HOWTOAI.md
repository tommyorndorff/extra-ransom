# How to Use AI Tools with This Repo

This is a Hugo static content site. AI assistants are most useful for editing Markdown content, maintaining consistency, and working with the Hugo configuration.

## Quick Start

```bash
make serve    # start local Hugo dev server (http://localhost:1313)
make build    # build to public/
make clean    # wipe build output
```

## What AI Can Help With

**Content editing**
- Drafting or refining pages under `content/docs/`
- Converting taper data into Markdown tables
- Improving clarity of build-log prose

**Hugo config**
- `config.yaml` controls theme, menus, and S3 deploy target
- Front matter fields: `title`, `weight`, `draft`, `bookCollapseSection`
- New pages: `hugo new docs/<name>.md` (uses `archetypes/default.md`)

**CI/CD**
- Workflow is `.github/workflows/workflow.yml`
- Secrets needed: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

## What to Avoid

- Do not modify files under `themes/` — it is a git submodule (`alex-shpak/hugo-book`).
- Do not commit to `public/` — it is build output, gitignored.
- `resources/_gen/` is Hugo's SCSS cache; `make clean` removes it.

## Project Context

See `AGENTS.md` for full architecture, conventions, and known limitations.
