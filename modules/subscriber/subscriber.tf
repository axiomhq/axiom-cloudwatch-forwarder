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

resource "aws_lambda_function" "subscriber" {
  s3_bucket     = var.mode == "dev" ? "axiom-cloudformation-dev" : "axiom-cloudformation"
  s3_key        = "axiom-cloudwatch-forwarder/v1.0"
  function_name = format("%s-subscriber", var.prefix)
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
  name = format("%s-subscriber-role", var.prefix)
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
    aws_iam_policy.subscriber.arn
  ]

  tags = {
    PartOf    = var.prefix
    Platform  = "Axiom"
    Component = "axiom-cloudwatch-subscriber"
  }
}

resource "aws_iam_policy" "subscriber" {
  name   = format("%s-subscriber-lambda-policy", var.prefix)
  path   = "/"
  policy = data.aws_iam_policy_document.subscriber.json
  tags = {
    PartOf    = var.prefix
    Platform  = "Axiom"
    Component = "axiom-cloudwatch-subscriber"
  }
}

resource "aws_cloudwatch_log_group" "subscriber" {
  name              = format("/aws/axiom/%s-subscriber", var.prefix)
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
