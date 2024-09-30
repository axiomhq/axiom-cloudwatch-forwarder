variable "prefix" {
  type        = string
  default     = "axiom-cloudwatch"
  description = "prefix for resources, defaults to axiom-cloudwatch"
}

variable "forwarder_lambda_arn" {
  type        = string
  description = "The ARN of the Lambda function that forwards logs to Axiom"
}

variable "log_groups_prefix" {
  type        = string
  description = "The prefix of the CloudWatch log groups that will trigger the Axiom CloudWatch Forwarder Lambda."
  default     = ""
}

variable "enable_cloudtrail" {
  type        = bool
  description = "Enable Cloudtrail for CloudWatch CreateLogGroup event notification? If already enabled, choose 'false'"
  default     = false
}

variable "mode" {
  type        = string
  default     = "prod"
  description = "mode for resources, defaults to prod"
}
