# AWS OIDC Setup for GitHub Actions

Configures short-lived AWS credentials for the deploy workflow via OpenID Connect federation. No long-lived access keys are stored as secrets.

## How it works

GitHub Actions mints a signed JWT for each job run. AWS verifies the token against GitHub's OIDC provider and issues temporary STS credentials scoped to the IAM role's permissions. The token expires when the job ends.

## Manual setup in the AWS console (learning exercise)

Worth doing by hand once, to see what the CloudFormation template below actually automates. If you just want a working deploy, skip to [CloudFormation](#cloudformation).

### 1. Create the OIDC identity provider

1. IAM console → **Identity providers** (left nav) → **Add provider**.
2. Provider type: **OpenID Connect**.
3. Provider URL: `https://token.actions.githubusercontent.com` (lowercase, exactly as shown). AWS fetches the TLS certificate thumbprint itself now — you won't be prompted to paste one in.
4. Audience: `sts.amazonaws.com`.
5. **Add provider**.

This provider is one-per-account, shared across every repo that federates through GitHub's OIDC issuer. If it already exists (from another project), reuse it and skip straight to step 2.

### 2. Create the IAM role

1. From the **Identity providers** list, open `token.actions.githubusercontent.com` and choose **Assign role** → **Create a new role** (or start from **Roles** → **Create role** and pick the provider there).
2. Trusted entity type: **Web identity**.
3. Identity provider: `token.actions.githubusercontent.com`. Audience: `sts.amazonaws.com`.
4. The console now exposes GitHub-specific fields right on this screen — fill them in instead of hand-editing trust policy JSON afterward:
   - **GitHub organization**: `tommyorndorff`
   - **GitHub repository** (optional): `extra-ransom`
   - **GitHub branch** (optional): `main`

   These map directly onto the `sub` claim condition (`repo:tommyorndorff/extra-ransom:ref:refs/heads/main`). IAM enforces that this condition can't be left as a bare wildcard for GitHub's OIDC provider — a trust policy that doesn't scope it will be rejected outright, not just flagged as a bad practice.
5. **Next**, then attach a permissions policy. Choose **Create policy** to open the JSON editor in a new tab and paste the `HugoDeploy` statement from the CloudFormation template below (S3 object/list access on the bucket, `cloudfront:CreateInvalidation` on the distribution). Return to this tab and select the policy you just created.
6. **Next.** Role name: `extra-ransom-github-deploy`. Review the summary — confirm the trust policy shows the scoped `sub` condition — then **Create role**.

### 3. Grab the role ARN

Open the role's summary page; the ARN is at the top (`arn:aws:iam::ACCOUNT_ID:role/extra-ransom-github-deploy`). Use it in [Update the workflow](#update-the-workflow) below.

## CloudFormation

The template below creates the same three resources by hand — useful for reuse or a second account once you've seen how the pieces fit together:
- The GitHub OIDC identity provider in your AWS account (one per account, shared across all repos)
- An IAM role trusted only by the `main` branch of this repo
- An inline policy with the minimum permissions `hugo deploy` requires

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: GitHub Actions OIDC role for extra-ransom Hugo deploy

Parameters:
  GitHubOrg:
    Type: String
    Default: tommyorndorff

  GitHubRepo:
    Type: String
    Default: extra-ransom

  RoleName:
    Type: String
    Default: extra-ransom-github-deploy

  CreateOIDCProvider:
    Type: String
    Default: 'true'
    AllowedValues: ['true', 'false']
    Description: >
      Set to false if the GitHub OIDC provider already exists in this account
      (only one can exist per provider URL per account).

Conditions:
  ShouldCreateOIDCProvider: !Equals [!Ref CreateOIDCProvider, 'true']

Resources:

  GitHubOIDCProvider:
    Type: AWS::IAM::OIDCProvider
    Condition: ShouldCreateOIDCProvider
    Properties:
      Url: https://token.actions.githubusercontent.com
      ClientIdList:
        - sts.amazonaws.com
      ThumbprintList:
        # GitHub's OIDC thumbprint — AWS validates against GitHub's JWKS endpoint
        # directly for this provider, so the value here is largely ceremonial.
        - 6938fd4d98bab03faadb97b34396831e3780aea1

  DeployRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Ref RoleName
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Federated: !Sub
                - 'arn:aws:iam::${AWS::AccountId}:oidc-provider/token.actions.githubusercontent.com'
                - {}
            Action: sts:AssumeRoleWithWebIdentity
            Condition:
              StringEquals:
                'token.actions.githubusercontent.com:aud': sts.amazonaws.com
              StringLike:
                # Scoped to main branch only. Change to `*` to allow any branch/tag.
                'token.actions.githubusercontent.com:sub': !Sub
                  - 'repo:${Org}/${Repo}:ref:refs/heads/main'
                  - Org: !Ref GitHubOrg
                    Repo: !Ref GitHubRepo
      Policies:
        - PolicyName: HugoDeploy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Sid: S3Deploy
                Effect: Allow
                Action:
                  - s3:PutObject
                  - s3:DeleteObject
                  - s3:GetObject
                  - s3:ListBucket
                Resource:
                  - !Sub 'arn:aws:s3:::www.${GitHubRepo}.net'
                  - !Sub 'arn:aws:s3:::www.${GitHubRepo}.net/*'
              - Sid: CloudFrontInvalidate
                Effect: Allow
                Action: cloudfront:CreateInvalidation
                Resource: !Sub 'arn:aws:cloudfront::${AWS::AccountId}:distribution/E2498U24MEPPED'

Outputs:
  RoleArn:
    Description: Role ARN to use in the GitHub Actions workflow
    Value: !GetAtt DeployRole.Arn
    Export:
      Name: !Sub '${AWS::StackName}-RoleArn'
```

Save this as `cfn-oidc.yaml` and deploy:

```bash
aws cloudformation deploy \
  --stack-name extra-ransom-oidc \
  --template-file cfn-oidc.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --profile your-admin-profile

# Get the role ARN from the stack output
aws cloudformation describe-stacks \
  --stack-name extra-ransom-oidc \
  --query 'Stacks[0].Outputs[?OutputKey==`RoleArn`].OutputValue' \
  --output text \
  --profile your-admin-profile
```

> If the GitHub OIDC provider already exists in your account (from another repo or prior setup), pass `--parameter-overrides CreateOIDCProvider=false` to skip creating it again.

## Update the workflow

In `.github/workflows/workflow.yml`, replace the `Configure AWS credentials` step with:

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::ACCOUNT_ID:role/extra-ransom-github-deploy
    aws-region: us-east-1
```

Remove the `aws-access-key-id` and `aws-secret-access-key` inputs entirely.

Add `id-token: write` to the job-level permissions block:

```yaml
permissions:
  contents: write
  id-token: write
```

Remove the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` repository secrets — they are no longer needed.

## Verifying it works

After merging and triggering a deploy run, the `Configure AWS credentials` step log should show:

```
Assuming role arn:aws:iam::ACCOUNT_ID:role/extra-ransom-github-deploy
```

If the trust condition is wrong (e.g. branch mismatch), the step fails with `AccessDenied` on `sts:AssumeRoleWithWebIdentity`. Double-check the `sub` claim matches the branch the workflow runs on.

## Hypothetical: hosting on Cloudflare instead (free tier)

Purely exploratory — not a recommendation to migrate, just answering "could this whole pipeline run for free on Cloudflare instead?" Short answer: yes, comfortably, at this site's scale.

**What it would replace**

- **Cloudflare Pages** (or **Workers with static assets** — Cloudflare's current default recommendation for *new* projects since Workers reached feature parity with Pages in 2026; Pages itself remains fully supported, no forced migration) replaces S3, CloudFront, and the OIDC role above entirely.
- Connect the GitHub repo, set the build command to `hugo --minify`, output directory `public`, and set a `HUGO_VERSION` build environment variable — Cloudflare's build image defaults to an old Hugo version otherwise.
- Cloudflare's git integration builds and deploys on every push by itself; the GitHub Actions workflow could shrink to nothing, or stay for unrelated checks.

**Why free covers this**

- Free plan: 500 builds/month (this repo pushes nowhere near 16/day), up to 100 custom domains per project, no published bandwidth cap for standard Pages/Workers hosting.
- The site serves from `www.extra-ransom.net` — a subdomain, not the bare apex `extra-ransom.net`. Cloudflare only requires delegating nameservers for the account when hosting an *apex* domain; a subdomain can be wired up with a single CNAME record, leaving the rest of the domain's DNS wherever it is today.

**What you'd give up**

- The CloudFront distribution (`E2498U24MEPPED`), the S3 bucket, and this entire OIDC setup become dead weight — including any AWS-specific familiarity gained from setting it up.
- Vendor lock-in shifts rather than disappears: AWS-shaped config (IAM policies, `hugo deploy` targets) gets replaced by Cloudflare-shaped config (build env vars, `_headers`/`_redirects` files).

**Smallest reversible way to test it**

Point a throwaway subdomain (e.g. `cf-test.extra-ransom.net`) at a Cloudflare Pages deployment of this same repo, without touching the live `www` CNAME or removing anything from AWS. That validates the build and hosting actually work before any real cutover decision.
