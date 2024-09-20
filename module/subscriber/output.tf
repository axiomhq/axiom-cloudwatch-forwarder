output "lambda_arn" {
  value = aws_lambda_function.subscriber.arn
}

output "log_groups_names" {
  value = var.log_groups_names
}

output "log_groups_prefix" {
  value = var.log_groups_prefix
}

output "log_groups_pattern" {
  value = var.log_groups_pattern
}
