# AWS Lambda

## Overview

Lambda is a **serverless, event-driven** compute service. You upload code and AWS runs it — no servers to provision or manage.

- Supported runtimes: Node.js, Python, Java, .NET, Go, Ruby, custom runtime (via Runtime API).
- Maximum execution timeout: **15 minutes**.
- Maximum memory: **10,240 MB** (10 GB); CPU scales with memory.
- Ephemeral storage: `/tmp` — **512 MB** to **10,240 MB**.
- Deployment package size: 50 MB (zipped), 250 MB (unzipped); use Lambda Layers for larger dependencies.

---

## Invocation Models

### Synchronous
- Caller **waits** for the response.
- Services: API Gateway, ALB, CloudFront (Lambda@Edge), Cognito, Lex, Alexa, Kinesis Data Firehose.
- Errors returned directly to the caller; no automatic retry by Lambda.

### Asynchronous
- Lambda **queues** the event and returns immediately (202).
- Services: S3, SNS, EventBridge, SES, CloudFormation, CodeCommit, CodePipeline.
- Lambda retries up to **2 times** on failure.
- Configure a **Dead Letter Queue** (SQS/SNS) for failed events.

### Event Source Mapping (Poll-based)
- Lambda **polls** the source and processes batches.
- Sources: **SQS**, **Kinesis Data Streams**, **DynamoDB Streams**, **MSK**, **MQ**.
- If processing fails, the batch is retried (use `bisectBatchOnError`, `maxRetryAttempts`, or DLQ to handle failures).

---

## Lambda Function Anatomy

```python
import json

def lambda_handler(event, context):
    # event: dict with trigger data
    # context: runtime info (function name, timeout remaining, etc.)
    print(context.function_name)
    print(context.get_remaining_time_in_millis())
    return {
        "statusCode": 200,
        "body": json.dumps("Hello from Lambda!")
    }
```

---

## Environment Variables

- Key-value pairs injected at runtime.
- Can be encrypted with **KMS**.
- Accessed via `os.environ['KEY']` (Python) or `process.env.KEY` (Node.js).
- Max total size: 4 KB.

---

## Versions & Aliases

### Versions
- Publishing a version creates an **immutable** snapshot (`$LATEST` is mutable).
- Each version has its own ARN.

### Aliases
- Pointers to specific versions (e.g., `PROD` → v3, `DEV` → $LATEST).
- Support **weighted traffic routing** (e.g., 90% → v3, 10% → v4) for canary deployments.
- Aliases have their own ARN.

---

## Concurrency

### Reserved Concurrency
- Guarantees a maximum number of concurrent executions for a function.
- Also acts as a throttle — requests exceeding this limit are **throttled**.

### Provisioned Concurrency
- Pre-warms execution environments to eliminate **cold starts**.
- Charged even when idle.

### Concurrency Limits
- Default: 1,000 concurrent executions per region (soft limit, can be increased).
- Throttled invocations return HTTP **429** (Too Many Requests).

---

## Cold Starts

- A cold start occurs when a new execution environment is initialised.
- Initialization code (outside the handler) runs only on cold start.
- Mitigation:
  - Use Provisioned Concurrency.
  - Use `SnapStart` for Java (Lambda takes a snapshot of the initialised environment).
  - Keep the deployment package small; minimise initialisation code.

---

## VPC Configuration

- Lambda runs outside your VPC by default.
- To access private resources (RDS, ElastiCache), configure Lambda to run in a **VPC**.
- Lambda creates an **ENI** in the specified subnets.
- Internet access from a VPC-attached Lambda requires a **NAT Gateway** (not an Internet Gateway).

---

## Lambda Layers

- Shared code/libraries packaged separately.
- Each function can reference up to **5 layers**.
- Layers are extracted to `/opt` in the execution environment.
- Useful for common dependencies (AWS SDK, utility libraries).

---

## Lambda Extensions

- Run alongside Lambda functions to integrate monitoring, security, or governance tools.
- Internal extensions: part of the runtime process.
- External extensions: separate process that runs before and after the handler.

---

## Lambda@Edge & CloudFront Functions

| Feature | Lambda@Edge | CloudFront Functions |
|---------|-------------|----------------------|
| Runtime | Node.js, Python | JavaScript |
| Trigger | Viewer/origin request & response | Viewer request & response |
| Max duration | 5–30 seconds | < 1 ms |
| Network access | Yes | No |
| Use case | Complex auth, A/B testing | Header manipulation, redirects |

---

## Destinations

- For **asynchronous** invocations: route successful or failed events to SQS, SNS, Lambda, or EventBridge.
- Preferred over DLQ because you get the full event context, not just the metadata.

---

## Pricing

- **Requests**: first 1M free, $0.20 per 1M thereafter.
- **Duration**: based on GB-seconds (memory × time); first 400,000 GB-seconds free per month.

---

## Exam Tips

- Lambda execution role is the IAM role that the function **assumes** (allows Lambda to call AWS services).
- Resource-based policies allow **other services/accounts** to invoke Lambda.
- Use **environment variables** for configuration; use **Secrets Manager** or **SSM Parameter Store** for secrets.
- `/tmp` storage persists across invocations within the same execution environment (warm container).
- Increasing memory is the only way to get more CPU; there is no direct CPU control.
- SQS as an event source: Lambda **polls** the queue; unprocessed messages return to the queue or go to a DLQ after `maxReceiveCount`.
