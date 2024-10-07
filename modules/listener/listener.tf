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

resource "aws_lambda_function" "listener" {
  s3_bucket     = var.forwarder_bucket
  s3_key        = "axiom-cloudwatch-forwarder/v${var.forwarder_version}/forwarder.zip"
  function_name = format("%s-listener", var.prefix)
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
  count         = var.enable_cloudtrail ? 1 : 0
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.listener.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.logs.arn
}

resource "aws_iam_role" "listener" {
  name = format("%s-listener-role", var.prefix)
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
    aws_iam_policy.listener.arn
  ]

  tags = {
    PartOf    = var.prefix
    Platform  = "Axiom"
    Component = "axiom-cloudwatch-listener"
  }
}

resource "aws_iam_policy" "listener" {
  name   = format("%s-listener-lambda-policy", var.prefix)
  path   = "/"
  policy = data.aws_iam_policy_document.listener.json
  tags = {
    PartOf    = var.prefix
    Platform  = "Axiom"
    Component = "axiom-cloudwatch-listener"
  }
}

resource "aws_cloudwatch_log_group" "listener" {
  name              = format("/aws/axiom/%s-listener", var.prefix)
  retention_in_days = 1
  tags = {
    PartOf    = var.prefix
    Platform  = "Axiom"
    Component = "axiom-cloudwatch-listener"
  }
}

data "aws_iam_policy_document" "cloudtrail" {
  count = var.enable_cloudtrail ? 1 : 0
  statement {
    sid    = "AWSCloudTrailAclCheck20150319"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
    actions   = ["s3:GetBucketAcl"]
    resources = [aws_s3_bucket.cloudtrail[0].arn]
  }
  statement {
    sid    = "AWSCloudTrailWrite20150319"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
    actions = ["s3:PutObject"]
    resources = [
      format("%s/AWSLogs/%s/*", aws_s3_bucket.cloudtrail[0].arn, data.aws_caller_identity.current.account_id)
    ]
    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-acl"
      values   = ["bucket-owner-full-control"]
    }
  }
}

resource "aws_s3_bucket_policy" "cloudtrail" {
  count      = var.enable_cloudtrail ? 1 : 0
  depends_on = [aws_s3_bucket.cloudtrail]
  bucket     = aws_s3_bucket.cloudtrail[0].id
  policy     = data.aws_iam_policy_document.cloudtrail[0].json
}


resource "aws_s3_bucket" "cloudtrail" {
  count = var.enable_cloudtrail ? 1 : 0
  # aws_s3_bucket_acl    = "BucketOwnerFullControl"
  bucket = format("%s-cloudtrail", var.prefix)

  tags = {
    PartOf    = var.prefix
    Platform  = "Axiom"
    Component = "axiom-cloudwatch-listener"
  }
}


// TODO:
// - Cloudformation has IsLogging: true, but no idea what does it do
// - Maybe we can make use event_selector to use cost?
resource "aws_cloudtrail" "cloudtrail" {
  count                         = var.enable_cloudtrail ? 1 : 0
  name                          = format("%s-cloudtrail", var.prefix)
  depends_on                    = [aws_s3_bucket.cloudtrail]
  enable_log_file_validation    = false
  s3_bucket_name                = aws_s3_bucket.cloudtrail[0].id
  include_global_service_events = false
}

resource "aws_cloudwatch_event_rule" "logs" {
  name        = format("%s-log-groups-auto-subscription-rule", var.prefix)
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
