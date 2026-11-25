# extra-ransom

The content and code for the [extra-ransom](https://www.extra-ransom.net) website: a build-log and knowledge base for split-cane bamboo fly-rod making, plus fishing trips, woodworking, coffee roasting, hydroponics and miscellany. This repo builds the site, not the AWS infrastructure under it.

Built with [Astro](https://astro.build) and [Starlight](https://starlight.astro.build). See `AGENTS.md` for the full project layout and conventions.

## Development

Requires Node 22.

```bash
npm ci            # install dependencies
npm run dev       # local dev server at http://localhost:4321
npm run build     # production build into dist/ (Pagefind search index + internal link check)
npm run preview   # serve dist/ locally
```

## Adding Content

Pages are Markdown files under `src/content/docs/docs/<section>/`, served at `/docs/<section>/<page>/`. Sections: `rods-and-fishing/` (`making/`, `trips/`), `woodworking/`, `coffee-roasting/`, `hydroponics/`, `miscellany/`. A directory's landing page is its `index.md`.

```yaml
---
title: "My Page"       # page title (rendered by Starlight; don't repeat it as an H1)
sidebar:
  order: 10            # lower = higher in the sidebar
draft: true            # unfinished pages are left out of the build; remove to publish
---
```

Sections list their pages in the sidebar automatically; a new subdirectory needs an entry in `astro.config.mjs`. When you move or rename a published page, add the old URL to `src/redirects.json`.

**Static assets** (images, PDFs, STLs): place in `public/static/<topic>/` and reference as `/static/<topic>/filename.ext`.

**Diagrams** are static SVGs in `public/goat/`, embedded as `![diagram](/goat/<name>.svg)`. They were rendered from GoAT ASCII art once; to make another, install the `goat` binary (`go install github.com/blampe/goat/cmd/goat@latest`), run `goat diagram.txt > public/goat/<name>.svg`, and embed it as an image.

**External links**: pair with a Wayback Machine archive URL for long-term stability.

**Standalone pages** (self-contained HTML/CSS/JS, no Starlight) live in `public/<name>/` and are linked from the home page's "Standalone pages" grid:

- [`/warbirds/`](https://www.extra-ransom.net/warbirds/) — *Mustang & Company*, an interactive P-51 and WWII aircraft explorer.
- [`/salamanders/`](https://www.extra-ransom.net/salamanders/) — *Salamanders of Western North Carolina*, a herpetology reference. Its [methods & re-run workbook](https://www.extra-ransom.net/salamanders/methods.html) explains how it was researched and how to update it; photo tooling is in `tools/salamanders/photos.py`.
- `/frame-calc/` (picture frame calculator), `/couch-to-5k/` (training calendar) and `/norway/`.

When you change a standalone page's CSS/JS, bump the `?v=YYYYMMDD` query strings in its HTML (those assets are cached immutably for a year).

## Deploy

On merge to `main`, GitHub Actions builds and deploys automatically:

```
github repo => npm run build => dist/ =>
  s3://www.extra-ransom.net =>
    cloudfront distribution E2498U24MEPPED
  (and the gh-pages branch)
```

The S3 sync gives hashed assets a 1-year immutable cache and everything else, including Pagefind's fixed-name search files, `max-age=0, must-revalidate`. There is no separate manual deploy command; to push by hand, build and run the two `aws s3 sync` passes from `.github/workflows/workflow.yml` with the `extra-ransom` AWS profile.

### AWS credentials for CI

**Recommended: OIDC (no long-lived keys).** See [`docs/aws-oidc-setup.md`](docs/aws-oidc-setup.md) for the full CloudFormation template and workflow changes.

**Fallback: IAM access key.** Create an IAM user with the minimum policy below and store the credentials as `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` repository secrets, then replace the OIDC step in the workflow with a key-based credentials step.

Minimum IAM policy (same permissions are used by both approaches):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3Deploy",
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:DeleteObject", "s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::www.extra-ransom.net",
        "arn:aws:s3:::www.extra-ransom.net/*"
      ]
    },
    {
      "Sid": "CloudFrontInvalidate",
      "Effect": "Allow",
      "Action": "cloudfront:CreateInvalidation",
      "Resource": "arn:aws:cloudfront::ACCOUNT_ID:distribution/E2498U24MEPPED"
    }
  ]
}
```
