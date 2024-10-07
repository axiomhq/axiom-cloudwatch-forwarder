variable "prefix" {
  type        = string
  default     = "axiom-cloudwatch"
  description = "Prefix for resources, defaults to axiom-cloudwatch"
}

variable "lambda_zip_bucket" {
  type        = string
  description = "Name of the S3 bucket where Lambda code is stored"
  default     = "axiom-cloudformation"
}

variable "lambda_zip_version" {
  type        = string
  description = "Version of the Axiom Lambda"
  default     = "1.2.0"
}

variable "forwarder_lambda_arn" {
  type        = string
  description = "The ARN of the Lambda function that forwards logs to Axiom"
}

variable "log_groups_prefix" {
  type        = string
  description = "The prefix of the CloudWatch log groups that will trigger the Axiom CloudWatch Forwarder Lambda"
  default     = ""
}
