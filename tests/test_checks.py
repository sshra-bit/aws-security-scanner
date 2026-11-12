"""Tests run against moto, a fake AWS, so they cost nothing and need no account."""

import json
import sys
from pathlib import Path

import boto3
from moto import mock_aws

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from checks import check_public_s3_buckets  # noqa: E402

FULL_BLOCK = {
    "BlockPublicAcls": True,
    "IgnorePublicAcls": True,
    "BlockPublicPolicy": True,
    "RestrictPublicBuckets": True,
}


def _session():
    return boto3.Session(region_name="us-east-1")


@mock_aws
def test_private_bucket_has_no_findings():
    s3 = _session().client("s3")
    s3.create_bucket(Bucket="private-bucket")
    s3.put_public_access_block(Bucket="private-bucket", PublicAccessBlockConfiguration=FULL_BLOCK)

    assert check_public_s3_buckets(_session()) == []


@mock_aws
def test_bucket_without_block_public_access_is_flagged():
    s3 = _session().client("s3")
    s3.create_bucket(Bucket="unprotected-bucket")

    findings = check_public_s3_buckets(_session())

    assert len(findings) == 1
    assert findings[0]["severity"] == "MEDIUM"


@mock_aws
def test_public_policy_is_flagged_high():
    s3 = _session().client("s3")
    s3.create_bucket(Bucket="public-bucket")
    policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::public-bucket/*",
        }],
    }
    s3.put_bucket_policy(Bucket="public-bucket", Policy=json.dumps(policy))

    findings = check_public_s3_buckets(_session())

    assert any(f["severity"] == "HIGH" for f in findings)
