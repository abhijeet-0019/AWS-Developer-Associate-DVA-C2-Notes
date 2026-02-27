# CI/CD – CodeCommit, CodeBuild, CodeDeploy, CodePipeline

## Overview

AWS provides a fully managed CI/CD suite:

| Service | Role |
|---------|------|
| **CodeCommit** | Source control (Git repositories) |
| **CodeBuild** | Build and test |
| **CodeDeploy** | Deployment automation |
| **CodePipeline** | Orchestration of the full CI/CD pipeline |
| **CodeArtifact** | Package management (npm, Maven, pip, etc.) |
| **CodeGuru** | AI-powered code reviews and performance recommendations |

---

## CodeCommit

### Overview
- Managed **Git** repository service hosted on AWS.
- Private, encrypted, and integrated with IAM.
- No size limit on repositories; supports standard Git workflows.

### Authentication
| Method | Usage |
|--------|-------|
| **HTTPS** | Git credentials (IAM user-specific) or AWS CLI credential helper |
| **SSH** | Upload SSH public key to IAM user profile |
| **HTTPS GRC** | git-remote-codecommit helper (recommended; works with IAM roles, MFA) |

### Security
- Encryption in transit (HTTPS/SSH) and at rest (AWS KMS).
- IAM policies control access; cannot use resource-based policies like GitHub.
- No public access — authentication required for all operations.
- **Trigger**: invoke Lambda or SNS on repository events (push, PR creation, etc.).
- **Notifications**: send to SNS or Chatbot via CloudWatch Events rules.

---

## CodeBuild

### Overview
- Fully managed **build service** — compiles source code, runs tests, and produces artifacts.
- Scales automatically; pay per build minute.
- No servers to manage.

### Build Process
1. Source: CodeCommit, S3, GitHub, Bitbucket, GitHub Enterprise.
2. CodeBuild pulls the source and the `buildspec.yml`.
3. Runs the build in a managed **Docker container**.
4. Artifacts uploaded to **S3**; logs to **CloudWatch Logs** and/or **S3**.

### buildspec.yml

```yaml
version: 0.2

env:
  variables:
    MY_VAR: "value"
  parameter-store:
    DB_PASSWORD: "/myapp/db/password"
  secrets-manager:
    API_KEY: "myapp/api-key:API_KEY"

phases:
  install:
    runtime-versions:
      python: 3.12
    commands:
      - pip install -r requirements.txt
  pre_build:
    commands:
      - echo "Running tests..."
      - pytest tests/
  build:
    commands:
      - echo "Building..."
      - python setup.py bdist_wheel
  post_build:
    commands:
      - echo "Build complete"

artifacts:
  files:
    - dist/*.whl
  discard-paths: yes

cache:
  paths:
    - /root/.cache/pip/**/*
```

### Key Points
- `buildspec.yml` must be at the **root** of the source directory (or specify a custom path).
- Build environment variables can come from plain text, **SSM Parameter Store**, or **Secrets Manager**.
- Supports **local builds** via Docker for testing (`codebuild_build.sh`).
- VPC support: run builds inside a VPC to access private resources.
- **Cache**: store reusable build dependencies in S3 (speeds up subsequent builds).

---

## CodeDeploy

### Overview
- Automates **application deployments** to EC2, on-premises servers, Lambda, and ECS.
- Manages rolling updates, blue/green deployments, and rollbacks.

### Deployment Targets

| Platform | Description |
|----------|-------------|
| **EC2 / On-premises** | Requires the **CodeDeploy Agent** to be installed and running |
| **Lambda** | Shifts traffic between function versions (canary, linear, all-at-once) |
| **ECS** | Blue/green deployments with ALB traffic shifting |

### appspec.yml

**For EC2/On-premises:**

```yaml
version: 0.0
os: linux
files:
  - source: /
    destination: /var/www/html
hooks:
  BeforeInstall:
    - location: scripts/before_install.sh
      timeout: 180
  AfterInstall:
    - location: scripts/after_install.sh
  ApplicationStart:
    - location: scripts/start_server.sh
  ValidateService:
    - location: scripts/validate.sh
```

**Lifecycle Hook Order (EC2):**
`ApplicationStop` → `DownloadBundle` → `BeforeInstall` → `Install` → `AfterInstall` → `ApplicationStart` → `ValidateService`

**For Lambda:**

```yaml
version: 0.0
Resources:
  - MyLambdaFunction:
      Type: AWS::Lambda::Function
      Properties:
        Name: MyFunction
        Alias: MyAlias
        CurrentVersion: "1"
        TargetVersion: "2"
Hooks:
  - BeforeAllowTraffic: ValidationHook
  - AfterAllowTraffic: ValidationHook
```

### Deployment Types

| Type | Description |
|------|-------------|
| **In-place** (Rolling) | Update instances in batches; instances briefly out of service |
| **Blue/Green** | New instances launched; traffic switched after validation; old instances terminated |

### Deployment Configurations

| Configuration | Description |
|---------------|-------------|
| `CodeDeployDefault.AllAtOnce` | Deploy to all instances at once |
| `CodeDeployDefault.HalfAtATime` | Deploy to half the instances |
| `CodeDeployDefault.OneAtATime` | Deploy to one instance at a time (slowest, safest) |
| Custom | Specify minimum healthy percentage |

### Rollbacks
- Automatic rollback on deployment failure or CloudWatch alarm breach.
- Manual rollback: re-deploy a previous revision.
- Rollback deploys a **new deployment** (not undo); original deployment is not reversed.

---

## CodePipeline

### Overview
- Orchestrates the CI/CD pipeline across multiple stages.
- Fully managed; integrates with CodeCommit, CodeBuild, CodeDeploy, Elastic Beanstalk, ECS, CloudFormation, and third-party tools.

### Pipeline Structure

```
[Source] → [Build] → [Test] → [Deploy] → [Approval] → [Deploy Prod]
```

- Each stage has one or more **actions** that run sequentially or in parallel.
- **Artifacts** are passed between stages via **S3**.
- Each pipeline action is executed by an AWS service or a third-party provider.

### Stage Action Providers (Examples)
| Stage | Providers |
|-------|-----------|
| Source | CodeCommit, S3, GitHub, ECR |
| Build | CodeBuild, Jenkins |
| Test | CodeBuild, DeviceFarm |
| Deploy | CodeDeploy, Elastic Beanstalk, CloudFormation, ECS, S3 |
| Approval | Manual approval (SNS notification) |
| Invoke | Lambda |

### Manual Approval Action
- Pipeline pauses; SNS notification sent to approvers.
- Approver reviews (e.g., staging environment) and approves/rejects via console, CLI, or SNS.

### Events & Triggers
- Triggered automatically on source changes via **CloudWatch Events** (for CodeCommit, ECR) or webhooks (GitHub).
- Can be triggered manually or on a schedule.

---

## CodeArtifact

- Managed **artifact repository** compatible with npm, pip, Maven, Gradle, NuGet, etc.
- Proxies public registries (npmjs.com, PyPI, Maven Central) and caches packages.
- Teams pull internal or approved external packages from CodeArtifact.

---

## Exam Tips

- CodeDeploy agent must be installed and running on EC2/on-premises instances; it is **not** required for Lambda or ECS.
- The `appspec.yml` (CodeDeploy) and `buildspec.yml` (CodeBuild) must be in the **root** of the deployment/source package.
- CodePipeline uses **S3** to pass artifacts between stages — ensure the pipeline has permissions to the artifact bucket.
- A failed stage in CodePipeline stops the pipeline; subsequent stages are not executed.
- Manual approval in CodePipeline expires after **7 days** (default).
- CodeDeploy **blue/green** on EC2 replaces instances; blue/green on ECS shifts ALB traffic between target groups.
