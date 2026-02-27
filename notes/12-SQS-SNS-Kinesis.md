# SQS, SNS & Kinesis

## SQS – Simple Queue Service

### Overview
- Fully managed **message queue** service.
- Decouples producers and consumers.
- At-least-once delivery; messages can be delivered more than once.
- Retention: 1 minute – 14 days (default 4 days).
- Maximum message size: **256 KB**.

---

### Queue Types

| Feature | Standard Queue | FIFO Queue |
|---------|---------------|-----------|
| Throughput | Unlimited | 300 msg/s (3,000 with batching) |
| Ordering | Best-effort | Strict FIFO |
| Delivery | At-least-once | Exactly-once |
| Deduplication | No | Yes (5-minute dedup window) |
| Use case | High throughput, order not critical | Order-critical, no duplicates |

---

### Key Parameters

| Parameter | Description |
|-----------|-------------|
| **Visibility Timeout** | Time a message is hidden after being received (default 30 s; max 12 hours) |
| **Message Retention** | How long unprocessed messages are kept (1 min – 14 days) |
| **Delivery Delay** | Delay before a message is available (default 0 s; max 15 min) |
| **Receive Message Wait Time** | Long polling wait time (0 = short polling; max 20 s) |
| **Max Receive Count** | Number of times a message can be received before going to DLQ |

---

### Short Polling vs. Long Polling

- **Short Polling** (default): returns immediately, even if no messages (may return empty responses — wastes requests).
- **Long Polling** (recommended): waits up to 20 seconds for messages; reduces empty responses and cost.

---

### Dead Letter Queue (DLQ)

- Messages that fail processing `MaxReceiveCount` times are moved to a DLQ.
- Helps isolate problematic messages for debugging.
- DLQ must be the same type (Standard → Standard DLQ; FIFO → FIFO DLQ).
- **DLQ Redrive** – move messages from DLQ back to the source queue for reprocessing.

---

### Message Groups (FIFO)
- `MessageGroupId` – messages in the same group are processed in order.
- Multiple consumers can process different groups in parallel.

### Deduplication (FIFO)
- `MessageDeduplicationId` – duplicate messages with the same ID within a 5-minute window are discarded.
- **Content-based deduplication**: SHA-256 hash of the message body used as the dedup ID.

---

### SQS + Lambda
- Lambda **polls** SQS (event source mapping).
- Lambda scales based on queue depth (up to 1,000 concurrent executions for Standard; 1 per message group for FIFO).
- On batch failure, use `ReportBatchItemFailures` to partial-retry only failed messages.

---

### SQS Extended Client
- For messages larger than 256 KB, use the **SQS Extended Client Library**.
- Stores the message payload in S3; sends a reference in the SQS message.

---

## SNS – Simple Notification Service

### Overview
- Fully managed **pub/sub** messaging service.
- Publishers send messages to a **Topic**; all subscribers receive a copy.
- Maximum message size: **256 KB**.

---

### Subscribers

| Type | Details |
|------|---------|
| **SQS** | Queue receives the message |
| **Lambda** | Function is invoked |
| **HTTP/HTTPS** | Webhook endpoint |
| **Email / Email-JSON** | Send to email addresses |
| **SMS** | Text message |
| **Kinesis Data Firehose** | Stream to S3, Redshift, etc. |
| **Mobile push** | APNS, GCM/FCM, ADM |

---

### SNS + SQS Fan-Out Pattern
- Publish once to SNS topic → deliver to multiple SQS queues simultaneously.
- Decouples event processing; each queue can have independent consumers.

---

### Message Filtering
- Subscribers can set a **filter policy** (JSON) to receive only matching messages.
- Filtering is by message attributes.

---

### FIFO Topics
- Strict ordering and exactly-once delivery (only SQS FIFO queues can subscribe).
- Lower throughput than Standard SNS topics.

---

### SNS Message Delivery Retries
- For HTTP/HTTPS endpoints: exponential back-off with up to 23 retries over 23 days.
- SQS/Lambda subscriptions: managed by those services.
- Configure a **DLQ** on the SNS subscription (not the topic) for failed HTTP deliveries.

---

## Kinesis

### Overview
- Platform for **real-time streaming** data ingestion and processing.
- Four services under the Kinesis umbrella:

| Service | Purpose |
|---------|---------|
| **Kinesis Data Streams** | Real-time data ingestion and custom processing |
| **Kinesis Data Firehose** | Load streaming data into S3, Redshift, OpenSearch, Splunk |
| **Kinesis Data Analytics** | SQL queries on streaming data |
| **Kinesis Video Streams** | Video streaming for ML/analysis |

---

### Kinesis Data Streams (KDS)

#### Shards
- A stream is divided into **shards** (the base unit of capacity).
- **Write**: 1 MB/s or 1,000 records/s per shard.
- **Read**: 2 MB/s per shard (shared across all consumers).
- Scale by adding shards (shard splitting) or removing shards (shard merging).

#### Records
- **Partition Key** – determines which shard the record goes to (hash function).
- **Sequence Number** – unique ID assigned by Kinesis.
- **Data Blob** – up to 1 MB.
- Retention: 1 day (default) – 365 days.

#### Consumers
| Type | Throughput | Fan-out |
|------|-----------|---------|
| **Standard (GetRecords)** | 2 MB/s per shard shared | All consumers share |
| **Enhanced Fan-out (SubscribeToShard)** | 2 MB/s per shard per consumer | Dedicated throughput per consumer |

#### Kinesis Producers
- **AWS SDK / KPL (Kinesis Producer Library)**: batching, compression, retries.
- `PutRecord` – single record.
- `PutRecords` – up to 500 records in one API call.

#### KCL – Kinesis Client Library
- Java library to build consumer applications.
- Each shard is processed by exactly one KCL worker at a time.
- Tracks progress (checkpointing) using **DynamoDB**.

---

### Kinesis Data Firehose (KDF)

- **Near-real-time** delivery (buffering: min 60 seconds or 1 MB).
- Destinations: **S3**, **Redshift** (via S3), **OpenSearch**, **Splunk**, **HTTP endpoints**.
- Optional transformations via **Lambda** before delivery.
- Fully managed, auto-scaling; no shards to manage.
- No replay capability (unlike KDS).

---

### Kinesis vs. SQS

| Feature | SQS | Kinesis Data Streams |
|---------|-----|---------------------|
| Ordering | FIFO only (FIFO queues) | Per-shard ordering |
| Consumers | One consumer per message | Multiple consumers |
| Replay | No (once consumed, gone) | Yes (within retention period) |
| Scalability | Unlimited (automatic) | Manual shard management |
| Latency | Milliseconds | Milliseconds |
| Retention | Up to 14 days | 1–365 days |

---

## Exam Tips

- SQS is a **pull** model (consumer polls); SNS is a **push** model (SNS pushes to subscribers).
- Use **SNS + SQS fan-out** to send one event to multiple downstream consumers.
- SQS Visibility Timeout should be longer than the consumer's processing time; if not, the message will be received again before processing finishes.
- Kinesis shard capacity is provisioned (not automatic) — you must plan for peak throughput.
- For ordering in SQS FIFO, use the same `MessageGroupId`; for parallelism, use different `MessageGroupId` values.
- **Hot shard problem** in Kinesis: distribute partition keys evenly to avoid all data going to one shard.
