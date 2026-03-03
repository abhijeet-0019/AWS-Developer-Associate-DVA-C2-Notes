Objective:
- VPC with public-private subnet in Production.

Steps:
- the vpc has public subnets and private subnets in two AZ
- each ppublic subet contains a NAT gateway and a load balancer node
- the servers eun in the private subents, are launched and terminated by using an asg, and receive traffince from the loadbalancer
- the servers can connect to the internet by using the NAT gateway.

CloudFormation Template Plan:
- create a `templates/production-vpc.yml` file under this project and declare Parameters for CIDR blocks, AZs, instance types, key pair name, and desired capacity so the stack stays reusable.
- define Resources for `AWS::EC2::VPC`, two public subnets, two private subnets, route tables, internet gateway, NAT gateways (one per public subnet), load balancer, target group, listener, Auto Scaling launch template, Auto Scaling group, and security groups that isolate the tiers.
- add Outputs for VPC ID, subnet IDs, load balancer DNS, and Auto Scaling group name to quickly verify the deployment and plug other stacks into this network later.

Deploy via AWS SDK (Python/boto3 example):
1. optional but recommended: create and activate a Python virtual environment (`python -m venv .venv` then `source .venv/bin/activate` on macOS/Linux or `.venv\\Scripts\\activate` on Windows) before installing `boto3` so project dependencies stay isolated.
2. install the SDK: `pip install boto3` (or the SDK of your preferred language).
3. ensure AWS credentials are configured locally (for example, run `aws configure` or set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION`).
4. run a short deployment script that calls `boto3.client("cloudformation").create_stack(...)` (or `update_stack`) while pointing `TemplateBody` to the contents of `templates/production-vpc.yml` and passing stack Parameters for AZs, key pair, etc.
5. poll `describe_stacks` until the status becomes `CREATE_COMPLETE`, then record the Outputs printed by the script for later use.
6. when changes are needed, update the template file and rerun the script with `update_stack` to keep everything managed as code instead of making console edits.

Virtual Environment Notes:
- not strictly required for using the SDK, but isolating dependencies with a virtual environment avoids version clashes between this project and other Python tools installed on your system.

