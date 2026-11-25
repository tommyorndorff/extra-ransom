# Contributing

This is a personal knowledge site for split-cane bamboo fly rod building. Contributions are not expected, but corrections to rod tapers, binder plans, or build notes are welcome via pull request.

## Making Changes

1. Fork the repo and create a branch from `main`.
2. Edit or add Markdown files under `src/content/docs/docs/`.
3. Run `npm ci && npm run dev` to preview locally at http://localhost:4321 (`npm run build` also checks internal links).
4. Submit a pull request — CI will build and deploy on merge to `main`.

## Content Guidelines

- Keep content factual and build-log oriented.
- Use `draft: true` in front matter for unfinished pages.
- Pair external links with Wayback Machine archive URLs where possible.
- Place static assets (photos, PDFs) in `public/static/<topic>/`.
