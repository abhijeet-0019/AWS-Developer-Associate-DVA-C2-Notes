# Monitoring – CloudWatch, X-Ray, CloudTrail

## CloudWatch

### Overview
- AWS's primary monitoring and observability service.
- Collects metrics, logs, and events; triggers alarms; visualizes dashboards.

---

### Metrics

- **Namespace**: group of related metrics (e.g., `AWS/EC2`, `AWS/Lambda`).
- **Dimension**: attribute used to filter/group metrics (e.g., `InstanceId`, `FunctionName`).
- **Resolution**: Standard (1-minute granularity) or High Resolution (1, 5, 10, 30-second granularity for custom metrics).
- EC2 default metrics: CPUUtilization, NetworkIn/Out, DiskRead/Write.
- EC2 **not** natively reported: Memory usage, disk space — requires the **CloudWatch Agent**.

#### Custom Metrics
- Publish via `PutMetricData` API.
- Standard resolution: `--storage-resolution 60` (default).
- High resolution: `--storage-resolution 1` (extra cost).

---

### CloudWatch Logs

- Collect logs from EC2 (via agent), Lambda, ECS, API Gateway, CloudTrail, Route 53, and more.
- **Log Group**: container for log streams (e.g., one per application/service).
- **Log Stream**: sequence of log events from a single source.
- **Retention**: set per log group (1 day to 10 years or never expire).

#### CloudWatch Logs Insights
- Interactive query language for log analysis.
- Query syntax similar to SQL; visualize results.

#### Subscriptions
- Real-time delivery of log events to:
  - **Lambda** (transformation/processing)
  - **Kinesis Data Streams / Firehose** (streaming)
  - **OpenSearch** (search and analysis)
- Use **Subscription Filters** to stream only matching log events.

#### CloudWatch Agent vs. Logs Agent
| Feature | Logs Agent | CloudWatch Agent |
|---------|-----------|-----------------|
| Send logs | Yes | Yes |
| Send metrics | No | Yes (memory, disk, etc.) |
| Configuration | Simple | More flexible (JSON config) |
| Recommendation | Legacy | Preferred |

---

### CloudWatch Alarms

- Monitor a single metric and trigger actions when thresholds are breached.
- States: `OK`, `ALARM`, `INSUFFICIENT_DATA`.
- Actions: SNS notifications, EC2 actions (stop/terminate/reboot/recover), Auto Scaling actions.
- **Composite Alarms**: combine multiple alarms with AND/OR logic to reduce alarm noise.
- **Alarm on metric math**: create alarms on expressions derived from multiple metrics.
- Period: minimum 10 s (high-resolution metrics) or 60 s (standard).

---

### CloudWatch Dashboards

- Visualize metrics and alarms across multiple services and regions on a single screen.
- Shareable with users inside and outside AWS.

---

### CloudWatch Events / EventBridge

- **EventBridge** (formerly CloudWatch Events) — event bus for AWS services and custom applications.
- Create **rules** to route events to targets (Lambda, SQS, SNS, Step Functions, etc.).
- **Event Pattern**: match specific event types (e.g., EC2 instance state change, CodeCommit push).
- **Scheduled Events**: cron or rate expressions to trigger targets on a schedule.
- **Event Bus**: default (AWS events) or custom (application events) or partner event sources.

---

## X-Ray

### Overview
- Distributed tracing service — visualize requests as they travel through microservices.
- Identify bottlenecks, errors, and latency across Lambda, EC2, ECS, API Gateway, SQS, SNS, DynamoDB, and more.

---

### Core Concepts

| Concept | Description |
|---------|-------------|
| **Trace** | End-to-end record of a request across all services |
| **Segment** | Work done by a single service (includes subsegments) |
| **Subsegment** | Granular information (outgoing HTTP calls, DB queries) |
| **Annotation** | Key-value pair indexed for filtering (use for searching traces) |
| **Metadata** | Key-value pair NOT indexed (any data type, for debugging) |
| **Sampling** | Control the percentage of requests traced (reduce cost) |

---

### Enabling X-Ray

#### EC2 / On-premises
1. Install and run the **X-Ray Daemon** (listens on UDP port 2000).
2. Use the X-Ray SDK in application code.

#### Lambda
- Enable **Active Tracing** in the Lambda configuration.
- X-Ray SDK available for code-level instrumentation.

#### ECS
- Run the X-Ray Daemon as a **sidecar container** in the task definition.
- Or use the Fargate-managed X-Ray integration.

#### Elastic Beanstalk
- Enable X-Ray via `.ebextensions` or the console.

---

### Sampling Rules

- Default: 1 req/sec + 5% of additional requests.
- Custom sampling rules: define reservoir (fixed rate) and rate in the console.
- Higher sampling = more data = higher cost.

---

### X-Ray API

- `PutTraceSegments` – upload segment documents.
- `PutTelemetryRecords` – upload telemetry (sampled/throttled counts).
- `GetSamplingRules` – retrieve sampling rules.

---

### X-Ray Groups

- Filter expressions to group traces for separate analysis and alerting.
- Can create CloudWatch Alarms based on X-Ray group metrics.

---

## CloudTrail

### Overview
- Records **API calls** made to AWS services — who, when, from where, and what action.
- Enabled by default; free for the last 90 days (management events).
- Store logs in **S3** and/or send to **CloudWatch Logs**.

---

### Event Types

| Type | Description |
|------|-------------|
| **Management Events** | Control plane operations (create/delete resources); enabled by default |
| **Data Events** | Data plane operations (S3 object-level, Lambda invocations); disabled by default (high volume) |
| **Insights Events** | Detect unusual API activity patterns; additional cost |

---

### Trail vs. Event History

| Feature | Event History | Trail |
|---------|--------------|-------|
| Retention | 90 days | Indefinite (stored in S3) |
| Cost | Free | S3 storage cost |
| Regions | Current region only | Single or all regions |
| CloudWatch integration | No | Yes |

---

### Multi-Region Trail

- A single trail that captures events from all regions.
- Recommended as best practice.

---

### CloudTrail Integration with CloudWatch

- Send CloudTrail events to CloudWatch Logs for real-time alerting.
- Create metric filters on specific API calls (e.g., alert on `DeleteBucket`).

---

## Exam Tips

- CloudWatch Logs: Lambda automatically integrates — logs are sent to a log group `/aws/lambda/{function-name}`.
- X-Ray does not trace **100%** of requests by default (sampling); enable custom rules for higher coverage.
- X-Ray **Annotations** are indexed and searchable; **Metadata** is not.
- CloudTrail logs who called an API; CloudWatch monitors **what** is happening (metrics/logs).
- To detect unusual activity across accounts, use **CloudTrail + Athena** for querying S3 logs, or enable **Insights Events**.
- The **X-Ray Daemon** must have the `xray:PutTraceSegments` and `xray:PutTelemetryRecords` IAM permissions.
- CloudWatch Alarms can automatically trigger **EC2 recovery** if the system check fails.
