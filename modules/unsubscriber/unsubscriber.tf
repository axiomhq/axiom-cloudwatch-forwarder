resource "aws_lambda_function" "unsubscriber" {
  s3_bucket     = var.lambda_zip_bucket
  s3_key        = "axiom-cloudwatch-forwarder/v${var.lambda_zip_version}/forwarder.zip"
  function_name = "${var.prefix}-unsubscriber"
  logging_config {
    log_format = "JSON"
    log_group  = aws_cloudwatch_log_group.unsubscriber.name
  }
  handler = "unsubscriber.lambda_handler"
  runtime = "python3.9"
  role    = aws_iam_role.unsubscriber.arn
  timeout = 300

  environment {
    variables = {
      "AXIOM_CLOUDWATCH_FORWARDER_LAMBDA_ARN" = var.forwarder_lambda_arn
    }
  }

  tags = {
    PartOf    = var.prefix
    Platform  = "Axiom"
    Component = "axiom-cloudwatch-unsubscriber"
  }
}

resource "aws_iam_role" "unsubscriber" {
  name = "${var.prefix}-unsubscriber-role"
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
    Component = "axiom-cloudwatch-unsubscriber"
  }
}

data "aws_iam_policy_document" "unsubscriber" {
  statement {
    actions = [
      "logs:DescribeSubscriptionFilters",
      "logs:DeleteSubscriptionFilter",
      "logs:PutSubscriptionFilter",
      "logs:DescribeLogGroups",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "lambda:AddPermission",
      "lambda:RemovePermission",
    ]

    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "unsubscriber" {
  name   = "default"
  role   = aws_iam_role.unsubscriber.id
  policy = data.aws_iam_policy_document.unsubscriber.json
}

resource "aws_cloudwatch_log_group" "unsubscriber" {
  name              = "/aws/axiom/${var.prefix}-unsubscriber"
  retention_in_days = 1
  tags = {
    PartOf    = var.prefix
    Platform  = "Axiom"
    Component = "axiom-cloudwatch-unsubscriber"
  }
}

resource "aws_lambda_invocation" "unsubscriber" {
  function_name = aws_lambda_function.unsubscriber.function_name
  input = jsonencode({
    CloudWatchLogGroupNames   = var.log_groups_names
    CloudWatchLogGroupPrefix  = var.log_groups_prefix
    CloudWatchLogGroupPattern = var.log_groups_pattern
  })
  lifecycle_scope = "CRUD"
}
