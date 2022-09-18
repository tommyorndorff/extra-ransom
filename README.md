# extra-ransom
## super-chainsaw

These names are from a project name generator and mean nothing.

The content in this repo builds the [extra-ransom: super-chainsaw](https://www.extra-ransom.net) website.  It doesnt build the infra.

On merge to main there are GH actions to deploy the site.
```
github repo =>
  s3://www.extra-ransom.net =>
    cloudfront distribution E2498U24MEPPED
```

To deploy manually with hugo, give it a `AWS_PROFILE=extra-ransom hugo deploy --maxDeletes -1 --force`