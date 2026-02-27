# DynamoDB

## Overview

DynamoDB is a fully managed **NoSQL** (key-value and document) database that delivers single-digit millisecond performance at any scale.

- Serverless, multi-AZ, automatically scales.
- Supports **ACID** transactions.
- Maximum item size: **400 KB**.

---

## Core Concepts

### Table
- Top-level entity; contains items (rows).

### Primary Key
| Type | Components | Use Case |
|------|-----------|----------|
| **Partition Key (PK)** | Single attribute | Uniform distribution required |
| **Composite Key (PK + SK)** | Partition Key + Sort Key | One-to-many relationships |

- Partition key determines which partition stores the item (hash function).
- Sort key allows range queries within a partition.

### Attributes
- Similar to columns; each item can have a different set of attributes (schema-less).
- Supported types: String, Number, Binary, Boolean, Null, List, Map, StringSet, NumberSet, BinarySet.

---

## Capacity Modes

### Provisioned Mode
- Specify **Read Capacity Units (RCU)** and **Write Capacity Units (WCU)** upfront.
- 1 RCU = 1 strongly consistent read (or 2 eventually consistent reads) for items up to 4 KB.
- 1 WCU = 1 write per second for items up to 1 KB.
- Auto-scaling adjusts capacity automatically.
- Cheaper for predictable workloads.

### On-Demand Mode
- No capacity planning; pay per request.
- Automatically scales to handle any traffic.
- Ideal for unpredictable or sporadic workloads (more expensive per request).

### Reserved Capacity
- Pre-purchase RCUs/WCUs for 1 or 3 years for significant savings.

---

## Indexes

### LSI – Local Secondary Index
- Same partition key as the table, **different sort key**.
- Must be defined at table creation time.
- Max 5 per table.
- Shares the provisioned capacity of the base table.

### GSI – Global Secondary Index
- **Different partition key and/or sort key**.
- Can be added at any time.
- Max 20 per table.
- Has its own provisioned/on-demand capacity.
- Supports only **eventual consistency**.

---

## Reading Data

### Eventually Consistent Read (default)
- Reads may not reflect the most recent write (replication lag possible).
- Costs 0.5 RCU per 4 KB.

### Strongly Consistent Read
- Always returns the most up-to-date data.
- Costs 1 RCU per 4 KB.
- Not supported on GSIs.
- Set `ConsistentRead=true` in API call.

### Transactional Read
- Costs 2 RCUs per 4 KB.

---

## Key API Operations

| Operation | Description |
|-----------|-------------|
| `PutItem` | Create or replace an item |
| `GetItem` | Read a single item by primary key |
| `UpdateItem` | Modify specific attributes; supports atomic counters |
| `DeleteItem` | Delete a single item |
| `Query` | Read items with a specific PK (and optional SK condition) |
| `Scan` | Read **all** items in a table (expensive; avoid in production) |
| `BatchGetItem` | Get multiple items (up to 100 / 16 MB) |
| `BatchWriteItem` | Put or delete multiple items (up to 25 / 16 MB) |
| `TransactGetItems` | Transactional reads (up to 25 items / 4 MB) |
| `TransactWriteItems` | Transactional writes (up to 25 items / 4 MB) |

---

## Conditional Writes

- Use `ConditionExpression` to write only if a condition is met (optimistic locking).

```python
table.put_item(
    Item={"pk": "user#1", "version": 2},
    ConditionExpression="version = :v",
    ExpressionAttributeValues={":v": 1}
)
```

---

## DynamoDB Streams

- Ordered stream of item-level changes (creates, updates, deletes).
- Records available for **24 hours**.
- Can trigger **Lambda** functions for real-time processing.
- View types: `KEYS_ONLY`, `NEW_IMAGE`, `OLD_IMAGE`, `NEW_AND_OLD_IMAGES`.

---

## DynamoDB Accelerator (DAX)

- In-memory **cache** for DynamoDB.
- Reduces latency from milliseconds to **microseconds**.
- Compatible with existing DynamoDB APIs (no application changes required).
- Cache for `GetItem` and `Query` calls; not for `Scan`.
- Cluster-based; lives in your VPC.

---

## TTL – Time to Live

- Automatically delete expired items at no extra cost (expires within 48 hours of TTL timestamp).
- Set a Number attribute (Unix epoch timestamp) as the TTL attribute.
- Expired items appear in reads until deleted; use a filter to exclude them.

---

## Backups

### On-Demand Backups
- Full backups at any time; no performance impact.

### Point-in-Time Recovery (PITR)
- Continuous backups for the last **35 days**.
- Restore to any second in the recovery window.
- Must be explicitly enabled.

---

## Global Tables

- Multi-region, multi-master replication.
- Requires DynamoDB Streams enabled.
- Low latency for globally distributed applications.
- Conflict resolution: **last-writer-wins**.

---

## Security

- Encryption at rest with **AWS KMS** (enabled by default).
- VPC Endpoints available for private access.
- IAM policies control access; use fine-grained access control with `dynamodb:LeadingKeys` condition.

---

## Exam Tips

- **Avoid Scan** – it reads the entire table and consumes RCUs; use Query or GSI instead.
- Use **GSI** to support alternative query patterns without restructuring the table.
- `ProjectionExpression` reduces the data returned (and the RCUs consumed).
- `FilterExpression` is applied after the query/scan – it does not reduce consumed capacity.
- For high-throughput writes, distribute across partition keys to avoid **hot partitions**.
- DAX is write-through; writes go to DynamoDB first, then DAX is updated.
- DynamoDB does **not** support joins or complex queries – design the data model for your access patterns.
