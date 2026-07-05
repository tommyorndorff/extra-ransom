# AWS OIDC Setup for GitHub Actions

Configures short-lived AWS credentials for the deploy workflow via OpenID Connect federation. No long-lived access keys are stored as secrets.

## How it works

GitHub Actions mints a signed JWT for each job run. AWS verifies the token against GitHub's OIDC provider and issues temporary STS credentials scoped to the IAM role's permissions. The token expires when the job ends.

## CloudFormation

The template below creates:
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
