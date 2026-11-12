# AWS Security Scanner

A serverless scanner that checks an AWS account for common security risks. Built with Python, AWS Lambda and Terraform.

> Work in progress. Built step by step as a learning project.

## Current checks

| Check | Severity | What it flags |
|---|---|---|
| Public S3 buckets | HIGH | Bucket policy or ACL allows public access |
| S3 Block Public Access | MEDIUM | Block Public Access is off or only partly on |

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q
aws sso login --profile scanner
python src/main.py --profile scanner
```

## Deploy to AWS

```powershell
cd terraform
terraform init
terraform plan
terraform apply
aws lambda invoke --function-name aws-security-scanner --profile scanner out.json
```

The Lambda uses a least-privilege IAM role with read-only access to the S3 settings it checks.
