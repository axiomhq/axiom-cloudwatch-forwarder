
data "archive_file" "unsubscriber" {
  type        = "zip"
  source_dir  = "${path.module}/../../src"
  output_path = "unsubscriber.zip"
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

resource "aws_lambda_function" "unsubscriber" {
  filename      = "unsubscriber.zip"
  function_name = format("%s-unsubscriber", var.prefix)
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
  name = format("%s-unsubscriber-role", var.prefix)
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

  managed_policy_arns = [
    aws_iam_policy.unsubscriber.arn
  ]

  tags = {
    PartOf    = var.prefix
    Platform  = "Axiom"
    Component = "axiom-cloudwatch-unsubscriber"
  }
}

resource "aws_iam_policy" "unsubscriber" {
  name   = format("%s-unsubscriber-lambda-policy", var.prefix)
  path   = "/"
  policy = data.aws_iam_policy_document.unsubscriber.json
  tags = {
    PartOf    = var.prefix
    Platform  = "Axiom"
    Component = "axiom-cloudwatch-unsubscriber"
  }
}

resource "aws_cloudwatch_log_group" "unsubscriber" {
  name              = format("/aws/axiom/%s-unsubscriber", var.prefix)
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
}
