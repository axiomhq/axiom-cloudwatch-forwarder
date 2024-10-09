resource "aws_lambda_function" "subscriber" {
  s3_bucket     = var.lambda_zip_bucket
  s3_key        = "axiom-cloudwatch-forwarder/v${var.lambda_zip_version}/forwarder.zip"
  function_name = "${var.prefix}-subscriber"
  logging_config {
    log_format = "JSON"
    log_group  = aws_cloudwatch_log_group.subscriber.name
  }
  handler = "subscriber.lambda_handler"
  runtime = "python3.9"
  role    = aws_iam_role.subscriber.arn
  timeout = 300

  environment {
    variables = {
      "AXIOM_CLOUDWATCH_FORWARDER_LAMBDA_ARN" = var.forwarder_lambda_arn
    }
  }

  tags = {
    PartOf    = var.prefix
    Platform  = "Axiom"
    Component = "axiom-cloudwatch-subscriber"
  }
}

resource "aws_iam_role" "subscriber" {
  name = "${var.prefix}-subscriber-role"
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
    Component = "axiom-cloudwatch-subscriber"
  }
}

data "aws_iam_policy_document" "subscriber" {
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

resource "aws_iam_role_policy" "subscriber" {
  name   = "default"
  role   = aws_iam_role.subscriber.id
  policy = data.aws_iam_policy_document.subscriber.json
}

resource "aws_cloudwatch_log_group" "subscriber" {
  name              = "/aws/axiom/${var.prefix}-subscriber"
  retention_in_days = 1
  tags = {
    PartOf    = var.prefix
    Platform  = "Axiom"
    Component = "axiom-cloudwatch-subscriber"
  }
}

resource "aws_lambda_invocation" "subscriber" {
  function_name = aws_lambda_function.subscriber.function_name
  input = jsonencode({
    CloudWatchLogGroupNames   = var.log_groups_names
    CloudWatchLogGroupPrefix  = var.log_groups_prefix
    CloudWatchLogGroupPattern = var.log_groups_pattern
  })
  lifecycle_scope = "CRUD"
}
