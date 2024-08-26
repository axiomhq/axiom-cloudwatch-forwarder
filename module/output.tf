output "forwarder_lambda" {
  value = aws_lambda_function.forwarder.arn
}

output "log_group_names" {
  value = var.log_group_names
}
