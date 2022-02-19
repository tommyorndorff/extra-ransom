---
title: Now that it builds...
date: "2022-02-19T15:10:10Z"
---

First we need an AWS IAM policy.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::www.hostname.com",
                "arn:aws:s3:::www.hostname.com/*",
            ]
        },
        {
            "Effect": "Allow",
            "Action": "s3:ListAllMyBuckets",
            "Resource": "arn:aws:s3:::*"
        }
    ]
}
```
Then create an IAM user credential that is dedicated to github actions.

We add some steps to our Github Actions `workflow.yml` to [set aws credentials, sync to s3, then invalidate our cloudfront distribution](https://github.com/tommyorndorff/extra-ransom/blob/1fd05de5a13e889051581ef907119703a29d3b8b/.github/workflows/workflow.yml#L36).

la fin. 🧑‍🌾