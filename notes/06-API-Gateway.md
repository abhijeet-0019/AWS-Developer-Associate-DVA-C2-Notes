# API Gateway

## Overview

API Gateway is a fully managed service for creating, publishing, and securing APIs at any scale.

- Supports **REST API**, **HTTP API**, and **WebSocket API**.
- Integrates with Lambda, HTTP endpoints, and AWS services directly.
- Handles throttling, authorization, caching, and monitoring.

---

## API Types Comparison

| Feature | REST API | HTTP API | WebSocket API |
|---------|----------|----------|---------------|
| Cost | Higher | ~70% cheaper | - |
| Latency | Higher | Lower | - |
| Authorization | IAM, Cognito, Lambda Authorizer, API key | IAM, Cognito, Lambda Authorizer, JWT | IAM, Lambda Authorizer |
| Usage Plans | Yes | No | No |
| Response Caching | Yes | No | No |
| Private integrations | Yes | Yes | No |
| AWS service proxy | Yes | No | No |

---

## Endpoint Types

| Type | Description |
|------|-------------|
| **Edge-Optimized** | Default; routes through CloudFront edge locations |
| **Regional** | For clients in the same region; can be combined with CloudFront |
| **Private** | Accessible only within a VPC via an interface VPC endpoint |

---

## Integration Types

| Type | Description |
|------|-------------|
| **Lambda Proxy** | Request/response passed as-is to Lambda; Lambda returns full HTTP response |
| **Lambda (non-proxy)** | API Gateway transforms request/response via mapping templates |
| **HTTP Proxy** | Passes request to an HTTP endpoint unchanged |
| **HTTP (non-proxy)** | API Gateway transforms request/response |
| **AWS Service** | Direct integration with AWS services (e.g., SQS, DynamoDB) |
| **Mock** | Returns a static response without calling a backend |

---

## Deployment Stages

- APIs must be **deployed** to a stage before they are accessible.
- Common stages: `dev`, `staging`, `prod`.
- Each stage has its own URL: `https://{api-id}.execute-api.{region}.amazonaws.com/{stage}`
- **Stage variables** – environment-specific configuration values (like environment variables for stages).
- **Canary deployments** – route a percentage of traffic to a new version of the stage.

---

## Authorizers

### IAM Authorization
- Requires caller to sign requests with AWS credentials (SigV4).
- Use for internal AWS services or cross-account access.

### Cognito User Pool Authorizer
- Validates JWT tokens issued by a Cognito User Pool.
- Simple to set up for user authentication.

### Lambda Authorizer (Custom Authorizer)
- Lambda function evaluates the request and returns an IAM policy.
- Two types:
  - **Token-based** – validates a bearer token (JWT, OAuth).
  - **Request-based** – inspects headers, query parameters, or context variables.
- Result can be cached (TTL 0–3600 s).

---

## Throttling

- **Account-level limit**: 10,000 req/s by default (soft limit).
- **Stage/method-level limits**: can be set per stage or per method.
- **Usage Plans**: define quotas and throttle limits per API key (for monetization/rate limiting).
- Throttled requests return **HTTP 429** (Too Many Requests).

---

## Caching

- Enabled per stage; cache capacity 0.5 GB – 237 GB.
- Default TTL: 300 seconds (max 3600 s).
- Clients can bypass the cache with `Cache-Control: max-age=0` (requires appropriate authorization).
- Not available for HTTP API.

---

## Mapping Templates

- Used in non-proxy integrations to transform request/response.
- Written in **Velocity Template Language (VTL)**.
- Can rename/reshape fields, filter data, or set defaults.

---

## CORS

- Must be enabled on API Gateway when the API is called from a browser on a different domain.
- API Gateway adds the necessary CORS headers.
- For Lambda Proxy integrations, the Lambda function must also return the CORS headers.

---

## WebSocket API

- Maintains a persistent connection between client and server.
- Use cases: real-time apps (chat, gaming, live dashboards).
- Routes based on a **route selection expression** (e.g., `$request.body.action`).
- Special routes: `$connect`, `$disconnect`, `$default`.
- Connections stored in DynamoDB; push messages to clients via the `@connections` management API.

---

## Logging & Monitoring

- **CloudWatch Metrics**: `Count`, `Latency`, `IntegrationLatency`, `4XXError`, `5XXError`.
- **Access Logging**: log request details to CloudWatch Logs (enable per stage).
- **Execution Logging**: detailed request/response logging (useful for debugging; disable in production to avoid high costs).
- **X-Ray**: enable active tracing to trace requests end-to-end.

---

## Exam Tips

- API Gateway has a **max integration timeout of 29 seconds** — Lambda functions running longer will cause a 504 error.
- Use **stage variables** instead of hardcoding stage-specific values (e.g., Lambda function alias, backend URL).
- **Resource Policies** allow controlling access at the API level (e.g., restrict to specific IPs or VPCs).
- Lambda Proxy integration is the most common pattern for REST APIs; it is simpler and more flexible.
- Billing is based on the number of API calls and data transfer; HTTP API is significantly cheaper than REST API.
