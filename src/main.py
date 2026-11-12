"""Run the scanner locally: python src/main.py --profile scanner"""

import argparse
import json

import boto3

from checks import check_public_s3_buckets


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="scanner")
    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile)
    findings = check_public_s3_buckets(session)

    print(json.dumps(findings, indent=2))
    print(f"\n{len(findings)} finding(s)")


if __name__ == "__main__":
    main()
