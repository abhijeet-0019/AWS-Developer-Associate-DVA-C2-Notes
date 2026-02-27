# Elastic Beanstalk

## Overview

Elastic Beanstalk is a **PaaS** (Platform-as-a-Service) that automatically handles deployment, scaling, load balancing, and health monitoring. You upload your application code and Beanstalk handles the rest.

- Supports: Node.js, Python, Ruby, PHP, Go, Java, .NET, Docker.
- Free to use — you pay only for the underlying AWS resources (EC2, RDS, etc.).
- Ideal for developers who want to focus on code, not infrastructure.

---

## Core Components

### Application
- Top-level container for environments and versions.

### Application Version
- A specific version of the deployable code (stored in S3).
- Multiple versions can exist simultaneously.

### Environment
- A collection of AWS resources running one application version.
- Types:
  - **Web Server Environment** – handles HTTP requests (EC2 + ALB + ASG).
  - **Worker Environment** – processes background jobs from an **SQS queue**.

### Environment Tier
| Tier | Use Case |
|------|----------|
| **Web Server** | Frontend / API serving HTTP traffic |
| **Worker** | Background processing, async tasks |

---

## Deployment Strategies

| Strategy | Downtime | Extra Cost | Rollback |
|----------|----------|------------|---------|
| **All at once** | Yes | None | Manual re-deploy |
| **Rolling** | No | None | Manual re-deploy |
| **Rolling with additional batch** | No | Yes (extra instances during deployment) | Manual re-deploy |
| **Immutable** | No | Yes (doubles fleet temporarily) | Fast (terminate new ASG) |
| **Traffic splitting** | No | Yes | Automatic (reroute traffic) |
| **Blue/Green** | No | Yes (parallel environment) | Fast (swap URLs) |

### Deployment Details

- **All at once**: deploys to all instances simultaneously. Fastest but causes brief outage. Best for dev.
- **Rolling**: updates instances in batches. No downtime but capacity is reduced during update.
- **Rolling with additional batch**: adds extra instances first, then rolls update. Full capacity maintained.
- **Immutable**: launches a new ASG with new instances; swaps when healthy. Safest; best for production.
- **Traffic splitting**: canary testing — routes a configurable percentage to new version.
- **Blue/Green**: create a new environment, test, then use **Route 53 / CNAME swap** to switch traffic.

---

## Configuration Files (.ebextensions)

- YAML/JSON files in a `.ebextensions/` folder at the root of your app package.
- Configure environment resources, set environment variables, install packages, run commands.

```yaml
# .ebextensions/options.config
option_settings:
  aws:autoscaling:asg:
    MinSize: 2
    MaxSize: 4
  aws:elasticbeanstalk:environment:proxy:
    ProxyServer: nginx
```

---

## Environment Properties & Secrets

- Set environment variables in the EB console or via `.ebextensions`.
- Reference secrets from **Secrets Manager** or **SSM Parameter Store** in `.ebextensions` or application code.

---

## Platforms

- **Managed platforms** – AWS-maintained (most common); select language/version.
- **Custom platforms** – build your own AMI using **Packer** for unsupported runtimes.
- **Docker**:
  - Single container: `Dockerfile` or `Dockerrun.aws.json` v1.
  - Multi-container (on ECS): `Dockerrun.aws.json` v2.

---

## Lifecycle Policy

- Elastic Beanstalk stores application versions in S3.
- Configure a **lifecycle policy** to automatically delete old versions (by count or age) to avoid hitting the 1,000-version limit.

---

## Health Monitoring

- **Basic health monitoring**: checks every 30 seconds; reports OK/Warning/Degraded/Severe.
- **Enhanced health monitoring**: detailed metrics for each instance and the environment (requires the health agent on the instance).
- Publishes metrics to **CloudWatch**.

---

## Cloning Environments

- Clone an existing environment to create an identical copy (same configuration).
- Useful for spinning up a staging environment that mirrors production.

---

## Rolling Back Deployments

| Strategy | Rollback Method |
|----------|----------------|
| All at once | Re-deploy previous version |
| Rolling | Re-deploy previous version (partial rollback risk) |
| Immutable | Terminate new ASG; traffic returns to original ASG |
| Blue/Green | Swap URLs back to the old (blue) environment |

---

## Exam Tips

- Elastic Beanstalk uses **CloudFormation** under the hood to provision resources.
- For **zero-downtime** deployments, use **Immutable** or **Rolling with additional batch**.
- The `.ebextensions` folder must be at the **root** of the application ZIP file.
- Beanstalk does **not** manage database lifecycle during environment teardown by default — use a separate RDS instance outside Beanstalk for persistence.
- Worker environments use a **daemon** process that polls an SQS queue; the `aws-sqsd` daemon comes pre-installed on worker AMIs.
- `eb deploy` deploys the current version; `eb swap` swaps environment CNAMEs (blue/green).
