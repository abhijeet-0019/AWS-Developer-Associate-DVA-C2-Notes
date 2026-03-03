#!/usr/bin/env python
"""Utility to deploy the production VPC CloudFormation stack via boto3."""
from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Iterable, List

import boto3
from botocore.exceptions import ClientError


def parse_parameters(param_list: Iterable[str]) -> List[dict]:
    """Convert CLI Key=Value pairs into the structure CloudFormation expects."""
    # Users feed --parameter Key=Value, which CloudFormation requires as a dict list
    parameters = []
    for raw in param_list:
        if '=' not in raw:
            raise ValueError(f"Invalid parameter '{raw}'. Use the Key=Value format.")
        key, value = raw.split('=', 1)
        parameters.append({'ParameterKey': key, 'ParameterValue': value})
    return parameters


def stack_exists(client, stack_name: str) -> bool:
    # Helper guards whether we need create_stack or update_stack
    try:
        client.describe_stacks(StackName=stack_name)
        return True
    except ClientError as exc:
        message = exc.response.get('Error', {}).get('Message', '').lower()
        if 'does not exist' in message:
            return False
        raise


def wait_for_completion(client, stack_name: str, operation: str) -> None:
    # Native waiters poll CloudFormation until create/update finishes
    waiter_name = 'stack_{}_complete'.format('create' if operation == 'create' else 'update')
    waiter = client.get_waiter(waiter_name)
    print(f"Waiting for stack {operation} to finish...")
    waiter.wait(StackName=stack_name)


def deploy(stack_name: str, template_path: pathlib.Path, parameters: List[dict], capabilities: List[str]) -> None:
    # Read template from disk so we can pass the body inline (avoids S3 uploads for small templates)
    template_body = template_path.read_text()
    cfn = boto3.client('cloudformation')

    if stack_exists(cfn, stack_name):
        print(f"Stack '{stack_name}' exists; issuing update...")
        try:
            response = cfn.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=capabilities,
            )
            wait_for_completion(cfn, stack_name, 'update')
        except ClientError as exc:
            if 'No updates are to be performed' in str(exc):
                print('No changes detected in the template or parameters.')
                return
            raise
    else:
        print(f"Creating stack '{stack_name}'...")
        cfn.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=capabilities,
        )
        wait_for_completion(cfn, stack_name, 'create')

    outputs = cfn.describe_stacks(StackName=stack_name)['Stacks'][0].get('Outputs', [])
    if outputs:
        print('\nStack Outputs:')
        for output in outputs:
            print(f"- {output['OutputKey']}: {output['OutputValue']}")


def main(argv: list[str] | None = None) -> int:
    # CLI wrapper keeps the script reusable from shell or other tooling
    parser = argparse.ArgumentParser(description='Deploy the production VPC stack via CloudFormation.')
    parser.add_argument('--stack-name', required=True, help='Name of the CloudFormation stack to create or update.')
    parser.add_argument(
        '--template',
        default='templates/production-vpc.yml',
        type=pathlib.Path,
        help='Path to the CloudFormation template file.',
    )
    parser.add_argument(
        '--parameter',
        action='append',
        default=[],
        dest='parameters',
        help='Parameter overrides in Key=Value format. Repeat for multiple parameters.',
    )
    parser.add_argument(
        '--capability',
        action='append',
        default=[],
        dest='capabilities',
        help='CloudFormation capabilities to acknowledge (for example, CAPABILITY_IAM).',
    )

    args = parser.parse_args(argv)
    template_path = args.template
    if not template_path.exists():
        parser.error(f"Template file '{template_path}' does not exist.")

    try:
        deploy(
            stack_name=args.stack_name,
            template_path=template_path,
            parameters=parse_parameters(args.parameters),
            capabilities=args.capabilities,
        )
    except Exception as exc:  # pragma: no cover - helper script
        print(f"Deployment failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
