resource "aws_lambda_function" "listener" {
  s3_bucket     = var.lambda_zip_bucket
  s3_key        = "axiom-cloudwatch-forwarder/v${var.lambda_zip_version}/forwarder.zip"
  function_name = "${var.prefix}-listener"
  description   = "Axiom CloudWatch Automatic log groups listener lambda"
  logging_config {
    log_format = "JSON"
    log_group  = aws_cloudwatch_log_group.listener.name
  }
  handler = "listener.lambda_handler"
  runtime = "python3.9"
  role    = aws_iam_role.listener.arn
  timeout = 300

  environment {
    variables = {
      "AXIOM_CLOUDWATCH_FORWARDER_LAMBDA_ARN" = var.forwarder_lambda_arn
      "LOG_GROUP_PREFIX" : var.log_groups_prefix
    }
  }

  tags = {
    PartOf    = var.prefix
    Platform  = "Axiom"
    Component = "axiom-cloudwatch-listener"
  }
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromEventBridge-${var.prefix}"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.listener.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.logs.arn
}

resource "aws_iam_role" "listener" {
  name = "${var.prefix}-listener-role"
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
    Component = "axiom-cloudwatch-listener"
  }
}

data "aws_iam_policy_document" "listener" {
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
      "lambda:InvokeFunction",
      "lambda:GetFunction",
      "logs:DescribeLogStreams",
      "logs:DescribeSubscriptionFilters",
      "logs:FilterLogEvents",
      "logs:GetLogEvents",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = ["*"]
  }
}
resource "aws_iam_role_policy" "listener" {
  name   = "default"
  role   = aws_iam_role.listener.id
  policy = data.aws_iam_policy_document.listener.json
}

resource "aws_cloudwatch_log_group" "listener" {
  name              = "/aws/axiom/${var.prefix}-listener"
  retention_in_days = 1
  tags = {
    PartOf    = var.prefix
    Platform  = "Axiom"
    Component = "axiom-cloudwatch-listener"
  }
}

resource "aws_cloudwatch_event_rule" "logs" {
  name        = "${var.prefix}-log-groups-auto-subscription-rule"
  description = "Axiom log group auto subscription event rule."
  event_pattern = jsonencode({
    source      = ["aws.logs"]
    detail-type = ["AWS API Call via CloudTrail"]
    detail = {
      eventSource = ["logs.amazonaws.com"]
      eventName   = ["CreateLogGroup"]
    }
  })
}

resource "aws_cloudwatch_event_target" "listener" {
  target_id = aws_lambda_function.listener.function_name
  arn       = aws_lambda_function.listener.arn
  rule      = aws_cloudwatch_event_rule.logs.name
}
