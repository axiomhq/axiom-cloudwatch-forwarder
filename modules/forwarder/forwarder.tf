resource "aws_lambda_function" "forwarder" {
  s3_bucket     = var.lambda_zip_bucket
  s3_key        = "axiom-cloudwatch-forwarder/v${var.lambda_zip_version}/forwarder.zip"
  function_name = "${var.prefix}-forwarder"
  logging_config {
    log_format = "JSON"
    log_group  = aws_cloudwatch_log_group.forwarder.name
  }
  handler = "forwarder.lambda_handler"
  runtime = "python3.9"
  role    = aws_iam_role.forwarder.arn

  environment {
    variables = {
      AXIOM_TOKEN   = var.axiom_token
      AXIOM_DATASET = var.axiom_dataset
      AXIOM_URL     = var.axiom_url
    }
  }

  tags = {
    PartOf    = var.prefix
    Platform  = "Axiom"
    Component = "axiom-cloudwatch-forwarder"
  }
}

resource "aws_iam_role" "forwarder" {
  name = "${var.prefix}-forwarder-role"
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

  tags = {
    PartOf    = var.prefix
    Platform  = "Axiom"
    Component = "axiom-cloudwatch-forwarder"
  }
}

resource "aws_cloudwatch_log_group" "forwarder" {
  name              = "/aws/axiom/${var.prefix}-forwarder"
  retention_in_days = 1
  tags = {
    PartOf    = var.prefix
    Platform  = "Axiom"
    Component = "axiom-cloudwatch-forwarder"
  }
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.forwarder.function_name
  principal     = "logs.amazonaws.com"
  source_arn    = format("arn:aws:logs:%s:%s:log-group:*:*", data.aws_region.current.name, data.aws_caller_identity.current.account_id)
}
