"""AWS Lambda entry point. Lambda calls lambda_handler(event, context) on every run."""

import json

import boto3

from checks import check_public_s3_buckets


def lambda_handler(event, context):
    # No keys here: inside Lambda, boto3 uses the function's IAM execution role.
    findings = check_public_s3_buckets(boto3.Session())

    # print() output goes to CloudWatch Logs automatically.
    print(json.dumps({"finding_count": len(findings), "findings": findings}))

    return {"finding_count": len(findings), "findings": findings}
