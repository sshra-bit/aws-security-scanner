import sys
from pathlib import Path

import boto3
from moto import mock_aws

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from handler import lambda_handler  # noqa: E402


@mock_aws
def test_handler_returns_findings(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    boto3.client("s3", region_name="us-east-1").create_bucket(Bucket="unprotected-bucket")

    result = lambda_handler({}, None)

    assert result["finding_count"] == 1
    assert result["findings"][0]["resource"] == "unprotected-bucket"
