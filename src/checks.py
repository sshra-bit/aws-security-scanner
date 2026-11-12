"""Security checks. Each check takes a boto3 Session and returns a list of findings."""

from botocore.exceptions import ClientError

PUBLIC_GRANTEES = {
    "http://acs.amazonaws.com/groups/global/AllUsers",
    "http://acs.amazonaws.com/groups/global/AuthenticatedUsers",
}


def _finding(resource, severity, issue):
    return {"check": "s3_public_bucket", "resource": resource, "severity": severity, "issue": issue}


def check_public_s3_buckets(session):
    """Flag S3 buckets that are public, or not protected by Block Public Access."""
    s3 = session.client("s3")
    findings = []

    for bucket in s3.list_buckets().get("Buckets", []):
        name = bucket["Name"]

        # 1. Is the bucket policy public?
        try:
            status = s3.get_bucket_policy_status(Bucket=name)
            if status["PolicyStatus"]["IsPublic"]:
                findings.append(_finding(name, "HIGH", "Bucket policy allows public access"))
        except ClientError as e:
            if e.response["Error"]["Code"] != "NoSuchBucketPolicy":
                raise

        # 2. Does the ACL grant access to everyone?
        acl = s3.get_bucket_acl(Bucket=name)
        if any(g["Grantee"].get("URI") in PUBLIC_GRANTEES for g in acl["Grants"]):
            findings.append(_finding(name, "HIGH", "Bucket ACL grants public access"))

        # 3. Is Block Public Access fully turned on?
        try:
            config = s3.get_public_access_block(Bucket=name)["PublicAccessBlockConfiguration"]
            if not all(config.values()):
                findings.append(_finding(name, "MEDIUM", "Block Public Access is only partly enabled"))
        except ClientError as e:
            if e.response["Error"]["Code"] != "NoSuchPublicAccessBlockConfiguration":
                raise
            findings.append(_finding(name, "MEDIUM", "Block Public Access is not configured"))

    return findings
