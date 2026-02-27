# ECS & ECR

## ECS – Elastic Container Service

### Overview
- Fully managed container orchestration service.
- Runs Docker containers on AWS.
- Two launch types: **EC2** and **Fargate**.

---

### Core Concepts

#### Cluster
- Logical grouping of compute resources (EC2 instances or Fargate capacity).

#### Task Definition
- Blueprint for running containers (similar to a Docker Compose file).
- Defines: container image, CPU/memory, port mappings, environment variables, IAM roles, logging.

#### Task
- A running instance of a Task Definition.
- Can run one or more containers.

#### Service
- Ensures a specified number of task copies run at all times.
- Integrates with **Application Load Balancer (ALB)** for traffic distribution.
- Supports rolling updates and blue/green deployments (via CodeDeploy).

---

### Launch Types

#### EC2 Launch Type
- You manage EC2 instances (the cluster infrastructure).
- ECS Agent runs on each EC2 instance.
- Register instances to the cluster using the ECS-optimized AMI.
- Cost-effective for predictable, steady workloads.

#### Fargate Launch Type
- **Serverless** — no EC2 instances to manage.
- Specify CPU and memory in the Task Definition; AWS provisions the infrastructure.
- Pay per task (vCPU and memory used).
- Best for variable or burst workloads.

---

### IAM Roles in ECS

| Role | Purpose |
|------|---------|
| **ECS Task Role** | Permissions the container needs to call AWS APIs (e.g., S3, DynamoDB). Defined per task definition. |
| **ECS Task Execution Role** | Permissions for ECS to pull images from ECR, push logs to CloudWatch, retrieve secrets from Secrets Manager. |
| **EC2 Instance Profile** (EC2 launch only) | Allows the ECS Agent on the EC2 instance to communicate with ECS. |

---

### Networking Modes

| Mode | Description |
|------|-------------|
| **awsvpc** | Each task gets its own ENI and private IP (required for Fargate; recommended for EC2) |
| **bridge** | Docker's default; uses a virtual bridge network on the host |
| **host** | Bypasses Docker networking; uses the host's network directly |
| **none** | No network access |

---

### Data Volumes

- **EFS** – persistent, shared storage across tasks and AZs (supported with Fargate).
- **Bind mounts** – share data between containers in the same task.
- **Docker volumes** – managed by Docker on the EC2 host (not supported in Fargate).

---

### Load Balancing

- Use **Application Load Balancer (ALB)** for HTTP/HTTPS; supports dynamic port mapping.
- Use **Network Load Balancer (NLB)** for TCP/UDP or extreme performance.
- ALB + ECS Service = automatic target group registration/deregistration during deployments.

---

### Auto Scaling

- **Service Auto Scaling** – scales the number of tasks.
  - Target Tracking Scaling
  - Step Scaling
  - Scheduled Scaling
- **Cluster Auto Scaling** (EC2 only) – scales the underlying EC2 instances using a Capacity Provider.

---

### Logging

- Configure the `awslogs` log driver in the task definition to send logs to **CloudWatch Logs**.
- Fargate requires the Task Execution Role to have `logs:CreateLogStream` and `logs:PutLogEvents` permissions.

---

### ECS Anywhere

- Run ECS tasks on **on-premises** infrastructure outside of AWS.

---

## ECR – Elastic Container Registry

### Overview
- Fully managed Docker container image registry.
- Stores, versions, and manages container images.
- Integrates natively with ECS, EKS, and Lambda.

---

### Repository Types

| Type | Description |
|------|-------------|
| **Private** | Access controlled via IAM; cross-account access supported |
| **Public** | Images publicly available via ECR Public Gallery |

---

### Common Commands

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com

# Build and tag image
docker build -t my-app .
docker tag my-app:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest

# Push image
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest

# Pull image
docker pull 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
```

---

### Security
- Images are encrypted at rest with **KMS**.
- **Image scanning** – basic scanning (CVE) on push or on-demand; enhanced scanning with Amazon Inspector.
- **Lifecycle Policies** – automatically expire unused images to control storage costs.
- **Cross-account access** – grant access via repository-based resource policies.

---

## Exam Tips

- Use `awsvpc` networking mode to give each task a dedicated security group.
- Fargate does not support the `host` or `bridge` networking modes.
- The **Task Execution Role** is needed to pull images from ECR and write to CloudWatch; the **Task Role** is what the running application uses.
- ECS with CodeDeploy supports **blue/green deployments** using two ALB target groups.
- ECR is not global; images are stored in a specific region.
- Use ECR image **tags** (e.g., `:latest`, `:v1.2.3`) to version images; immutable tags prevent overwriting.
