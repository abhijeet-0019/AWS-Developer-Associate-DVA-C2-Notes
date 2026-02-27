# Security – KMS, Secrets Manager, SSM Parameter Store

## KMS – Key Management Service

### Overview
- Managed service to create and control **cryptographic keys** used to encrypt data.
- Integrated with most AWS services (S3, EBS, RDS, DynamoDB, Lambda, SQS, etc.).
- FIPS 140-2 Level 2 compliant (Level 3 for CloudHSM).

---

### Key Types

| Type | Description |
|------|-------------|
| **AWS Owned Keys** | Managed by AWS; no visibility or control; free |
| **AWS Managed Keys** | Created in your account by AWS services (e.g., `aws/s3`); auditable; no rotation control |
| **Customer Managed Keys (CMK)** | Created/managed by you; full control; $1/month + API charges |

### Key Material Origins
- **AWS KMS** – KMS generates and manages key material.
- **External (BYOK)** – Import your own key material.
- **AWS CloudHSM** – Key material stored in your CloudHSM cluster.

### Key Types by Algorithm
- **Symmetric** (AES-256) – single key for encrypt/decrypt (most common; required for envelope encryption).
- **Asymmetric** (RSA, ECC) – public/private key pair; public key can be downloaded; useful for external encryption.

---

### Key Rotation
- **AWS Managed Keys**: automatic rotation every 1 year (cannot disable).
- **Customer Managed Keys**: optional automatic rotation every 1 year; or manual rotation.
- Rotation creates a new key version; old versions kept to decrypt old data.

---

### Key Policies
- Resource-based policy on the KMS key (similar to S3 bucket policies).
- The **root account** must be given access in the key policy (otherwise the key becomes unmanageable).
- Without a key policy, no IAM policies can grant access to the key.

---

### Envelope Encryption

- Encrypting large data directly with KMS is impractical (4 KB API limit).
- **Envelope Encryption**:
  1. KMS generates a **Data Encryption Key (DEK)**.
  2. The DEK encrypts your plaintext data.
  3. KMS encrypts the DEK with the CMK (DEK is stored alongside the ciphertext).
  4. To decrypt: KMS decrypts the DEK → DEK decrypts the data.
- AWS Encryption SDK implements this pattern.

---

### KMS API

| API | Description |
|-----|-------------|
| `Encrypt` | Encrypt up to 4 KB of data |
| `Decrypt` | Decrypt ciphertext |
| `GenerateDataKey` | Returns plaintext DEK + encrypted DEK |
| `GenerateDataKeyWithoutPlaintext` | Returns only the encrypted DEK (for later use) |
| `ReEncrypt` | Decrypt and re-encrypt with a different key |
| `DescribeKey` | Get key metadata |
| `ListKeys` | List KMS keys |

---

### KMS Multi-Region Keys
- Primary key replicated to other regions.
- Same key ID, same key material across regions — decrypt in a different region than where it was encrypted.
- Not global; each replica is independent after creation.

---

### KMS Limits
- API request limits vary by region (e.g., 5,500–30,000 requests/sec for cryptographic operations).
- Use **DEKs** (envelope encryption) to avoid hitting KMS limits for high-volume encryption.

---

## Secrets Manager

### Overview
- Managed service to store, rotate, and retrieve secrets (database credentials, API keys, etc.).
- Tight integration with **RDS**, **Redshift**, **DocumentDB** for automatic rotation.
- Rotation uses a **Lambda function** to update the secret and the target service.

---

### Features

| Feature | Details |
|---------|---------|
| **Automatic Rotation** | Built-in rotation Lambdas for RDS (MySQL, PostgreSQL, Oracle, SQL Server, Aurora) |
| **Encryption** | Always encrypted with KMS (CMK or `aws/secretsmanager`) |
| **Versioning** | Multiple versions; labels: `AWSCURRENT`, `AWSPENDING`, `AWSPREVIOUS` |
| **Cross-Account** | Share secrets across accounts via resource-based policies |
| **Multi-Region** | Replicate secrets to other regions; read replicas automatically updated on rotation |

### Accessing Secrets

```python
import boto3
import json

client = boto3.client('secretsmanager', region_name='us-east-1')
response = client.get_secret_value(SecretId='myapp/db/credentials')
secret = json.loads(response['SecretString'])
db_password = secret['password']
```

### Pricing
- $0.40 per secret per month + $0.05 per 10,000 API calls.

---

## SSM Parameter Store

### Overview
- Managed storage for configuration data and secrets.
- Part of AWS Systems Manager.
- Hierarchical key-value store.

---

### Parameter Tiers

| Feature | Standard | Advanced |
|---------|----------|---------|
| Max size | 4 KB | 8 KB |
| Max parameters | 10,000 | Unlimited |
| Cost | Free | $0.05/parameter/month |
| Parameter policies | No | Yes (TTL, notifications) |
| Larger values | No | Yes |

### Parameter Types
- `String` – plain text.
- `StringList` – comma-separated values.
- `SecureString` – encrypted with KMS.

### Accessing Parameters

```bash
# Get a single parameter
aws ssm get-parameter --name "/myapp/db/password" --with-decryption

# Get parameters by path (hierarchy)
aws ssm get-parameters-by-path --path "/myapp/" --recursive --with-decryption
```

```python
import boto3

ssm = boto3.client('ssm')
param = ssm.get_parameter(Name='/myapp/db/password', WithDecryption=True)
password = param['Parameter']['Value']
```

### Parameter Policies (Advanced)
- **Expiration** – auto-delete parameter after a date (notify via EventBridge).
- **ExpirationNotification** – notify before expiry.
- **NoChangeNotification** – alert if a parameter hasn't changed within a period.

---

## Secrets Manager vs. SSM Parameter Store

| Feature | Secrets Manager | SSM Parameter Store |
|---------|----------------|---------------------|
| Primary use | Secrets with rotation | Configuration + secrets |
| Auto rotation | Yes (built-in Lambda) | No (manual) |
| Cost | $0.40/secret/month | Free (Standard) |
| Encryption | Always KMS | Optional (SecureString) |
| Cross-account | Yes | Yes |
| CloudFormation | Yes (`dynamic references`) | Yes (`dynamic references`) |
| Max size | 64 KB | 4 KB (Standard) / 8 KB (Advanced) |

---

## Other Security Services

### ACM – AWS Certificate Manager
- Provision, manage, and deploy **SSL/TLS certificates**.
- Free for certificates used with AWS services (ALB, CloudFront, API Gateway).
- Auto-renewal for ACM-managed certificates.
- Cannot export private keys for certificates provisioned by ACM.

### WAF – Web Application Firewall
- Protect web apps from common exploits (SQL injection, XSS, etc.).
- Deployed on: ALB, API Gateway, CloudFront, AppSync.
- Define **Web ACLs** with rules; supports rate limiting.
- **AWS Managed Rules**: pre-built rulesets for OWASP Top 10, bot control.

### Shield
- DDoS protection:
  - **Shield Standard** – automatic, free (all AWS customers).
  - **Shield Advanced** – $3,000/month; 24/7 DDoS response team, cost protection.

---

## Exam Tips

- **Secrets Manager** is for secrets that need automatic rotation; **SSM Parameter Store** is for configuration and simple secrets.
- Always use **envelope encryption** for data larger than 4 KB with KMS.
- The KMS key policy is required — even for the root account — to administer the key. Without it, the key can become unrecoverable.
- In CloudFormation, use **dynamic references** to pull secrets/parameters at deployment time:
  - `{{resolve:secretsmanager:MySecret:SecretString:password}}`
  - `{{resolve:ssm-secure:/myapp/db/password}}`
- For Lambda: retrieve secrets at **initialization** (outside the handler) and cache them; use `SecretRotation` event to refresh when a rotation occurs.
- KMS API calls are logged in **CloudTrail** — full audit trail of key usage.
