# extra-ransom
## super-chainsaw

These names are from a project name generator and mean nothing.

The content in this repo builds the [extra-ransom: super-chainsaw](https://www.extra-ransom.net) website. It doesn't build the infra.

## Development

Requires [Hugo](https://gohugo.io/installation/) (extended build, v0.163.3+):

```bash
make serve    # local dev server at http://localhost:1313
make build    # build to public/
make clean    # wipe build output
```

The theme (Hextra) is loaded via Hugo modules (`go.mod`) — no submodule init needed.

## Adding Content

All content lives under `content/docs/`. Each `.md` file becomes a page in the sidebar.

**New doc page:**
```bash
hugo new docs/my-page.md
```

**New rod build log** (appears under the Rod Builds section):
```bash
hugo new docs/rod-builds/my-rod.md
```

Both commands use `archetypes/default.md` to pre-fill front matter. Key fields:

```yaml
---
title: "My Page"       # sidebar label
weight: 10             # lower = higher in sidebar
draft: true            # set to false (or remove) to publish
---
```

Additional Hextra front matter options (uncomment to use):
- `sidebar.exclude: true` — hide from sidebar but still accessible by URL
- `toc: false` — disable the in-page table of contents

**Static assets** (images, PDFs): place in `static/static/<topic>/` and reference as `/static/<topic>/filename.ext`.

**External links**: pair with a Wayback Machine archive URL for long-term stability.

**Standalone pages** (self-contained HTML/CSS/JS, no Hugo templating) live in `static/<name>/` and are linked from the home page's "Standalone pages" grid:

- [`/warbirds/`](https://www.extra-ransom.net/warbirds/) — *Mustang & Company*, an interactive P-51 and WWII aircraft explorer.
- [`/salamanders/`](https://www.extra-ransom.net/salamanders/) — *Salamanders of Western North Carolina*, a herpetology reference. Its [methods & re-run workbook](https://www.extra-ransom.net/salamanders/methods.html) explains how it was researched and how to update it; photo tooling is in `tools/salamanders/photos.py`.

When you change a standalone page's CSS/JS, bump the `?v=YYYYMMDD` query strings in its HTML (those assets are cached immutably for a year).

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

### AWS credentials for CI

**Recommended: OIDC (no long-lived keys).** See [`docs/aws-oidc-setup.md`](docs/aws-oidc-setup.md) for the full CloudFormation template and workflow changes.

**Fallback: IAM access key.** Create an IAM user with the minimum policy below and store the credentials as `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` repository secrets. The current workflow reads those automatically.

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
