data "archive_file" "forwarder" {
  type        = "zip"
  source_file = "${path.module}/../src/forwarder.py"
  output_path = "forwarder.zip"
}

resource "aws_lambda_function" "forwarder" {
  filename      = "forwarder.zip"
  function_name = format("%s-forwarder", var.prefix)
  logging_config {
    log_format = "JSON"
    log_group  = aws_cloudwatch_log_group.forwarder.name
  }
  handler = "forwarder.handler"
  runtime = "python3.9"
  role    = aws_iam_role.forwarder.arn

  environment {
    variables = {
      AXIOM_TOKEN   = var.axiom_token
      AXIOM_DATASET = var.axiom_dataset
    }
  }
}

resource "aws_iam_role" "forwarder" {
  name = format("%s-forwarder-role", var.prefix)
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      },
    ]
  })
}

resource "aws_cloudwatch_log_group" "forwarder" {
  name              = format("/aws/axiom/%s-forwarder", var.prefix)
  retention_in_days = 1
}


resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.forwarder.function_name
  principal     = "logs.amazonaws.com"
  source_arn    = format("arn:aws:logs:%s:%s:log-group:*:*", data.aws_region.current.name, data.aws_caller_identity.current.account_id)
}


resource "aws_cloudwatch_log_subscription_filter" "forwarder" {
  for_each        = { for index, name in var.log_group_names : index => name }
  name            = format("%s-forwarder-%s", var.prefix, element(split("/", each.value), length(split("/", each.value)) - 1))
  log_group_name  = each.value
  filter_pattern  = ""
  destination_arn = aws_lambda_function.forwarder.arn
}
