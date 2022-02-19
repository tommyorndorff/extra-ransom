---
title: hi world; first post.
date: "2022-02-17T04:31:00.000Z"
description: "getting github actions to build"
---

alrighty, new/first post on my potentially useless blog.

first up, need something that looks nice so we can get inspired.  enter
[mcfarland's page](https://www.mcfarlandrods.com/gallery); surely that will work.

![mcfarland spruce creek](./mcfarland_spruce_creek.jpg)

OK, thats better.  Now, to find a Gatsby deployment process for github 
actions.  Here we go, [just a bit of Googlin'](https://github.com/marketplace/actions/gatsby-publish).

```yaml
name: Gatsby Publish

on:
  push:
    branches:
      - dev

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v1
      - uses: enriikke/gatsby-gh-pages-action@v2
        with:
          access-token: ${{ secrets.ACCESS_TOKEN }}
```
No idea how a github action works.  Looks like `yaml`, in a `./.github/workflows/workflow.yml` file.

Kind of awkward -- why there is an actions "marketplace" when that may lead to rogue code execution,
I have no idea.  But who am I to say thats wrong.  Right here, all I need are 
a build environment, node 14, gatsby build, then a couple aws cli commands
to push to s3 then invalidate cloudfront.

Thats it for now.  It builds when I push.