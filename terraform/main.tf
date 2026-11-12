terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

provider "aws" {
  region  = var.region
  profile = var.aws_profile
}

# Zip the Python code in src/ so Lambda can run it.
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/build/scanner.zip"
  excludes    = ["main.py", "__pycache__"]
}

# --- IAM: the role Lambda "wears" while it runs ---

# Trust policy: only the Lambda service may assume this role.
resource "aws_iam_role" "scanner" {
  name = "${var.project}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

# Lets Lambda write logs to CloudWatch.
resource "aws_iam_role_policy_attachment" "logs" {
  role       = aws_iam_role.scanner.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Least privilege: read-only access to exactly what the S3 check needs.
resource "aws_iam_role_policy" "s3_read" {
  name = "s3-security-read"
  role = aws_iam_role.scanner.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:ListAllMyBuckets",
        "s3:GetBucketAcl",
        "s3:GetBucketPolicyStatus",
        "s3:GetBucketPublicAccessBlock",
      ]
      Resource = "*"
    }]
  })
}

# --- Logs: keep 14 days so old logs don't cost money forever ---

resource "aws_cloudwatch_log_group" "scanner" {
  name              = "/aws/lambda/${var.project}"
  retention_in_days = 14
}

# --- The Lambda function ---

resource "aws_lambda_function" "scanner" {
  function_name    = var.project
  role             = aws_iam_role.scanner.arn
  runtime          = "python3.13"
  handler          = "handler.lambda_handler"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = 60
  memory_size      = 128

  depends_on = [aws_cloudwatch_log_group.scanner]
}
