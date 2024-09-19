data "aws_region" "current" {}

data "aws_caller_identity" "current" {}


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
