# CloudFormation & SAM

## CloudFormation

### Overview
- Infrastructure as Code (IaC) service; provision AWS resources using YAML or JSON templates.
- Manages resources as a **Stack** — create, update, and delete resources together.
- Free — pay only for the underlying resources created.

---

### Template Anatomy

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: "My CloudFormation Stack"

Parameters:
  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues: [t3.micro, t3.small]

Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-0abcdef1234567890

Conditions:
  IsProd: !Equals [!Ref Environment, "prod"]

Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-bucket"

Outputs:
  BucketName:
    Value: !Ref MyBucket
    Export:
      Name: !Sub "${AWS::StackName}-BucketName"
```

| Section | Required | Description |
|---------|----------|-------------|
| `AWSTemplateFormatVersion` | No | Template version (always `2010-09-09`) |
| `Description` | No | Human-readable description |
| `Parameters` | No | Input values at stack creation/update |
| `Mappings` | No | Static lookup tables |
| `Conditions` | No | Conditional resource creation |
| `Resources` | **Yes** | AWS resources to create |
| `Outputs` | No | Values to export to other stacks |

---

### Intrinsic Functions

| Function | Description |
|----------|-------------|
| `!Ref` | Reference a parameter or resource's default attribute |
| `!GetAtt` | Get a specific attribute of a resource |
| `!Sub` | String substitution |
| `!Join` | Join values with a delimiter |
| `!Select` | Select from a list by index |
| `!If` | Conditional value based on a Condition |
| `!ImportValue` | Import an exported value from another stack |
| `!FindInMap` | Look up a value in a Mapping |
| `!Base64` | Encode a string to Base64 (used for EC2 UserData) |

---

### Stack Operations

- **Create Stack**: provisions all resources in the template.
- **Update Stack**: computes a **Change Set** — preview changes before applying.
- **Delete Stack**: deletes all resources in the stack (unless DeletionPolicy is `Retain`).

### Change Sets
- Preview proposed changes before executing an update.
- Does not indicate if the update will succeed.

### Drift Detection
- Detects when actual resource configuration differs from the template.
- Highlights manual changes made outside CloudFormation.

---

### Stack Policies
- JSON policy that controls which resources can be updated or replaced during a stack update.
- Protects critical resources from accidental modification.

---

### Deletion Policies

| Policy | Effect |
|--------|--------|
| `Delete` | Delete the resource (default for most) |
| `Retain` | Keep the resource after stack deletion |
| `Snapshot` | Create a snapshot before deleting (RDS, EBS, Redshift) |

---

### DependsOn
- Explicitly define resource creation order.
- By default, CloudFormation determines the order automatically from `!Ref`/`!GetAtt` references.

---

### Nested Stacks
- Reuse common templates by referencing them as a resource of type `AWS::CloudFormation::Stack`.
- Good for modular architecture (network stack, compute stack, etc.).

### StackSets
- Deploy a single template across **multiple accounts and regions** simultaneously.
- Requires a delegated administrator account (or the management account in AWS Organizations).

---

### CloudFormation Rollback
- On creation failure: stack is rolled back (resources deleted) by default.
- On update failure: stack rolls back to the last known good state.
- Can disable rollback for debugging.

---

## SAM – Serverless Application Model

### Overview
- An **extension** of CloudFormation for serverless applications.
- Shorthand syntax to define Lambda, API Gateway, DynamoDB, and Step Functions.
- Transforms (`AWS::Serverless`) are processed by CloudFormation during deployment.

---

### SAM Template Structure

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Runtime: python3.12
    Timeout: 30
    Environment:
      Variables:
        TABLE_NAME: !Ref MyTable

Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.lambda_handler
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /hello
            Method: get

  MyTable:
    Type: AWS::Serverless::SimpleTable
    Properties:
      PrimaryKey:
        Name: id
        Type: String
```

### SAM Resource Types
| Type | Equivalent |
|------|------------|
| `AWS::Serverless::Function` | Lambda + IAM role + event source mappings |
| `AWS::Serverless::Api` | API Gateway REST API |
| `AWS::Serverless::HttpApi` | API Gateway HTTP API |
| `AWS::Serverless::SimpleTable` | DynamoDB table (single attribute PK) |
| `AWS::Serverless::StateMachine` | Step Functions state machine |
| `AWS::Serverless::LayerVersion` | Lambda Layer |

---

### SAM CLI Commands

| Command | Description |
|---------|-------------|
| `sam init` | Scaffold a new SAM application |
| `sam build` | Build the application and dependencies |
| `sam local invoke` | Invoke a Lambda function locally |
| `sam local start-api` | Run API Gateway locally |
| `sam local start-lambda` | Run a local Lambda endpoint |
| `sam deploy --guided` | Package and deploy to AWS |
| `sam logs` | Fetch CloudWatch logs |
| `sam validate` | Validate a SAM/CloudFormation template |

---

### SAM + CodeDeploy

- SAM natively integrates with CodeDeploy for **safe Lambda deployments**.
- Supports traffic shifting strategies:
  - `Canary10Percent5Minutes` – 10% for 5 min, then 100%
  - `Linear10PercentEvery1Minute` – 10% more every minute
  - `AllAtOnce` – all traffic at once

---

## Exam Tips

- CloudFormation **Resources** section is the only required section.
- Use `!Sub` instead of `!Join` for string interpolation — it is cleaner.
- `AWS::NoValue` removes a property when used in a Condition (e.g., `!If [Condition, value, !Ref AWS::NoValue]`).
- Outputs with `Export` can be imported in other stacks with `!ImportValue` — stack must be in the **same region**.
- SAM requires `Transform: AWS::Serverless-2016-10-31` at the top of the template.
- `sam deploy` packages code to S3 and creates/updates a CloudFormation stack.
