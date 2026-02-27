# IAM – Identity and Access Management

## Overview

IAM is a **global** service that controls authentication (who you are) and authorization (what you can do) in AWS.

---

## Core Components

### Users
- Represents a **person or application** that interacts with AWS.
- Has long-term credentials (password and/or access keys).
- Best practice: one IAM user per person; never share credentials.

### Groups
- A collection of IAM users.
- Policies are attached to groups, and users inherit them.
- A user can belong to multiple groups.
- Groups **cannot** contain other groups.

### Roles
- An IAM identity with permissions; **assumed** by trusted entities (users, services, accounts).
- No permanent credentials — temporary security credentials are issued via AWS STS.
- Common use cases:
  - EC2 instance role (access S3, DynamoDB, etc.)
  - Lambda execution role
  - Cross-account access

### Policies
- JSON documents that define **Allow** or **Deny** permissions.
- **Identity-based policies** – attached to users, groups, or roles.
- **Resource-based policies** – attached to resources (e.g., S3 bucket policy).
- **Permission boundaries** – set maximum permissions for an IAM entity.
- **Service Control Policies (SCP)** – used with AWS Organizations to restrict accounts.

---

## Policy Evaluation Logic

1. Default **Deny** (implicit deny for everything).
2. Evaluate all applicable policies.
3. An explicit **Deny** always overrides any **Allow**.
4. An explicit **Allow** grants access (unless an explicit Deny exists).

---

## Policy Structure

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "StringEquals": { "s3:prefix": "home/" }
      }
    }
  ]
}
```

Key elements:
| Element | Description |
|---------|-------------|
| `Version` | Policy language version (always `2012-10-17`) |
| `Statement` | Array of individual permission statements |
| `Effect` | `Allow` or `Deny` |
| `Action` | AWS API actions (e.g., `s3:GetObject`) |
| `Resource` | ARN of the resource(s) |
| `Condition` | Optional conditions (IP, MFA, time, etc.) |

---

## IAM Security Tools

| Tool | Purpose |
|------|---------|
| **IAM Credentials Report** | Account-level CSV listing all users and credential status |
| **IAM Access Advisor** | Shows service permissions and last accessed time (helps reduce permissions) |
| **Access Analyzer** | Identifies resources shared with external entities |

---

## Best Practices

- Enable **MFA** for the root account and all privileged users.
- Use **IAM Roles** for applications running on EC2 or Lambda (never hardcode keys).
- Grant **least privilege** – only the permissions needed.
- Use **groups** to manage permissions for sets of users.
- Rotate access keys regularly.
- Never use the **root account** for daily tasks.
- Monitor with **CloudTrail** for API call history.

---

## STS – Security Token Service

- Issues **temporary** credentials (Access Key ID, Secret Access Key, Session Token).
- Used when assuming roles.
- Key API calls:
  - `AssumeRole` – assume a role in the same or another account.
  - `AssumeRoleWithWebIdentity` – for federated users via web identity providers (replaced by Cognito).
  - `AssumeRoleWithSAML` – for SAML-based federation.
  - `GetSessionToken` – for MFA-protected operations.

---

## Cross-Account Access Pattern

1. Account A creates a role with a **trust policy** allowing Account B to assume it.
2. Account B user/service calls `sts:AssumeRole` with the role ARN.
3. STS returns temporary credentials for Account A resources.

---

## Exam Tips

- `iam:PassRole` permission is required to pass a role to an AWS service (e.g., EC2, Lambda).
- Resource-based policies do not require `sts:AssumeRole` – the principal directly accesses the resource.
- Permission boundaries limit the maximum permissions but do not grant permissions on their own.
- AWS-managed policies are convenient but may be overly permissive; prefer customer-managed policies for fine-grained control.
