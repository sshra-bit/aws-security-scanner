variable "project" {
  description = "Name used for the Lambda function and related resources"
  type        = string
  default     = "aws-security-scanner"
}

variable "region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS CLI profile to deploy with (your SSO profile)"
  type        = string
  default     = "scanner"
}
