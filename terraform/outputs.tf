output "lambda_function_name" {
  value = aws_lambda_function.scanner.function_name
}

output "log_group" {
  value = aws_cloudwatch_log_group.scanner.name
}
