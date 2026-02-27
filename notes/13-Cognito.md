# Cognito

## Overview

Amazon Cognito provides **authentication, authorization, and user management** for web and mobile applications without managing your own identity infrastructure.

Two main components:
1. **User Pools** – authenticate users (sign-up, sign-in, MFA).
2. **Identity Pools** (Federated Identities) – authorize users (grant temporary AWS credentials).

---

## Cognito User Pools (CUP)

### Overview
- A **serverless user directory** for web/mobile app users.
- Handles sign-up, sign-in, account recovery, email/phone verification, and MFA.
- Returns **JWT tokens** (ID token, access token, refresh token) on successful authentication.

### Features
- Built-in UI (Hosted UI) for sign-up/sign-in pages.
- Social sign-in: Google, Facebook, Amazon, Apple (via OIDC/SAML federation).
- **Lambda Triggers** – customize the auth flow with Lambda hooks.
- **Advanced Security** – detect compromised credentials, adaptive authentication.
- **User Pools** can be integrated directly with **API Gateway** as an authorizer.

### Lambda Triggers (Examples)
| Trigger | Description |
|---------|-------------|
| Pre Sign-up | Validate/transform user attributes before registration |
| Post Confirmation | Send welcome email after successful verification |
| Pre Authentication | Custom validation before sign-in |
| Post Authentication | Log successful sign-ins |
| Pre Token Generation | Customize token claims |
| Custom Message | Customize verification/MFA messages |
| Custom Auth Challenge | Implement custom auth flows (e.g., CAPTCHA) |

### User Pool Groups
- Assign users to groups; group membership included in the JWT token.
- Useful for role-based access in the application.

### Hosted UI
- Pre-built, customizable sign-in/sign-up pages hosted by Cognito.
- Supports custom domains (`auth.example.com`).
- Mandatory for social/SAML/OIDC federation.

---

## Cognito Identity Pools (Federated Identity)

### Overview
- Exchange third-party identity tokens (from User Pools, Google, Facebook, SAML, etc.) for **temporary AWS credentials** (via STS).
- Users get an IAM role to access AWS resources directly (e.g., S3, DynamoDB).

### Flow
1. User authenticates with an identity provider (e.g., Cognito User Pool) and receives a token.
2. App calls Identity Pool with the token.
3. Identity Pool validates the token and calls **STS AssumeRoleWithWebIdentity**.
4. STS returns temporary credentials.
5. App uses credentials to access AWS services directly.

### IAM Roles in Identity Pools
- **Authenticated role** – for signed-in users.
- **Unauthenticated (guest) role** – for unauthenticated users (limited access).
- Role-based access: assign different IAM roles to different user groups.

### Policy Variables (Fine-Grained Access)
- Use `${cognito-identity.amazonaws.com:sub}` in IAM policy conditions to restrict users to their own data.

```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::my-bucket/${cognito-identity.amazonaws.com:sub}/*"
}
```

---

## User Pools vs. Identity Pools

| Feature | User Pools | Identity Pools |
|---------|-----------|----------------|
| Purpose | Authentication (who you are) | Authorization (what you can do) |
| Output | JWT tokens | Temporary AWS credentials |
| AWS access | No (use Identity Pools for that) | Yes |
| Social federation | Yes | Yes |
| Unauthenticated access | No | Yes (guest role) |

---

## Common Architecture Patterns

### Pattern 1: User Pools + API Gateway
```
User → Cognito User Pool → JWT token → API Gateway (Cognito Authorizer) → Lambda
```

### Pattern 2: User Pools + Identity Pools + AWS Services
```
User → Cognito User Pool → JWT → Identity Pool → STS → Temp Credentials → S3/DynamoDB
```

### Pattern 3: Social Login
```
User → Google/Facebook → Social Token → Cognito User Pool (Federation) → JWT → App
```

---

## Exam Tips

- **User Pools** handle sign-up/sign-in and return JWT tokens; they do NOT grant direct access to AWS services.
- **Identity Pools** exchange identity tokens for temporary AWS credentials (STS).
- The combination of User Pools + Identity Pools is the standard pattern for mobile/web apps needing both authentication and AWS resource access.
- API Gateway supports **Cognito User Pool** as a built-in authorizer (validates JWT automatically).
- Cognito tokens: **ID token** (user attributes), **access token** (scopes/permissions), **refresh token** (obtain new tokens).
- Default token validity: ID/Access – 1 hour; Refresh – 30 days (configurable).
- **Pre Token Generation** Lambda trigger is used to add custom claims to the JWT.
