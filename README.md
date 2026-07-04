# extra-ransom
## super-chainsaw

These names are from a project name generator and mean nothing.

The content in this repo builds the [extra-ransom: super-chainsaw](https://www.extra-ransom.net) website. It doesn't build the infra.

## Development

Requires [Hugo](https://gohugo.io/installation/) and the hugo-book submodule:

```bash
git submodule update --init   # fetch hugo-book theme (first time)
make serve                    # local dev server at http://localhost:1313
make build                    # build to public/
make clean                    # wipe build output
```

## Adding Content

All content lives under `content/docs/`. Each `.md` file becomes a page in the sidebar.

**New doc page:**
```bash
hugo new docs/my-page.md
```

**New rod build log** (appears under the Projects section):
```bash
hugo new docs/projects/my-rod.md
```

Both commands use `archetypes/default.md` to pre-fill front matter. Key fields:

```yaml
---
title: "My Page"       # sidebar label
weight: 10             # lower = higher in sidebar
draft: true            # set to false (or remove) to publish
---
```

Additional hugo-book front matter options (uncomment to use):
- `bookCollapseSection: true` — collapse child pages under this section by default
- `bookHidden: true` — hide from sidebar but still accessible by URL
- `bookToc: false` — disable the in-page table of contents

**Static assets** (images, PDFs): place in `static/static/<topic>/` and reference as `/static/<topic>/filename.ext`.

**External links**: pair with a Wayback Machine archive URL for long-term stability.

Pages with `draft: true` are hidden in production but visible with `make serve` (which passes `--buildDrafts`).

## Deploy

On merge to `main`, GitHub Actions builds and deploys automatically:

```
github repo =>
  s3://www.extra-ransom.net =>
    cloudfront distribution E2498U24MEPPED
```

Manual deploy (requires `extra-ransom` AWS profile):

```bash
AWS_PROFILE=extra-ransom hugo deploy --maxDeletes -1 --force
```
