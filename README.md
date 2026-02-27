# AWS Developer Associate (DVA-C02) Exam Notes

A comprehensive collection of notes and study materials for the **AWS Certified Developer – Associate (DVA-C02)** certification exam.

---

## 📋 Exam Overview

| Detail | Info |
|--------|------|
| **Exam Code** | DVA-C02 |
| **Duration** | 130 minutes |
| **Questions** | 65 questions (multiple choice / multiple response) |
| **Passing Score** | 720 / 1000 |
| **Cost** | $150 USD |

## 📊 Exam Domains & Weightings

| Domain | Topic | Weight |
|--------|-------|--------|
| 1 | Development with AWS Services | 32% |
| 2 | Security | 26% |
| 3 | Deployment | 24% |
| 4 | Troubleshooting and Optimization | 18% |

---

## 📚 Notes Index

### Core Services
- [01 – IAM (Identity and Access Management)](notes/01-IAM.md)
- [02 – EC2 (Elastic Compute Cloud)](notes/02-EC2.md)
- [03 – S3 (Simple Storage Service)](notes/03-S3.md)
- [04 – DynamoDB](notes/04-DynamoDB.md)
- [05 – Lambda](notes/05-Lambda.md)
- [06 – API Gateway](notes/06-API-Gateway.md)

### Containers & PaaS
- [07 – ECS & ECR](notes/07-ECS-ECR.md)
- [08 – Elastic Beanstalk](notes/08-Elastic-Beanstalk.md)

### Infrastructure as Code & Deployment
- [09 – CloudFormation & SAM](notes/09-CloudFormation.md)
- [10 – CI/CD (CodeCommit, CodeBuild, CodeDeploy, CodePipeline)](notes/10-CICD.md)

### Observability
- [11 – Monitoring (CloudWatch, X-Ray, CloudTrail)](notes/11-Monitoring.md)

### Messaging & Streaming
- [12 – SQS, SNS & Kinesis](notes/12-SQS-SNS-Kinesis.md)

### Security
- [13 – Cognito](notes/13-Cognito.md)
- [14 – Security (KMS, Secrets Manager, SSM)](notes/14-Security.md)

---

## 🔑 Key Tips for the Exam

1. **Focus on Developer-centric services** – Lambda, API Gateway, DynamoDB, S3, and the CI/CD suite are heavily tested.
2. **Understand IAM thoroughly** – Policies, roles, and permission boundaries appear throughout all domains.
3. **Know the AWS SDKs & CLI** – Understand how credentials are resolved, pagination, and error handling.
4. **Serverless architecture** – Lambda + API Gateway + DynamoDB is a very common pattern in exam scenarios.
5. **CI/CD pipeline** – Be comfortable with each stage: source (CodeCommit), build (CodeBuild), deploy (CodeDeploy), and orchestrate (CodePipeline).
6. **Encryption** – Know when to use KMS, client-side encryption, envelope encryption, and Secrets Manager vs. SSM Parameter Store.
7. **CloudWatch vs X-Ray** – CloudWatch for metrics/logs/alarms; X-Ray for distributed tracing.

---

## 📖 Recommended Resources

- [AWS Official Exam Guide (DVA-C02)](https://d1.awsstatic.com/training-and-certification/docs-dev-associate/AWS-Certified-Developer-Associate_Exam-Guide.pdf)
- [AWS Developer Documentation](https://docs.aws.amazon.com/)
- [AWS Free Tier](https://aws.amazon.com/free/) – Practice hands-on

---

## 🤝 Contributing

Feel free to open a PR to add or improve notes. Please keep entries concise, accurate, and exam-focused.
