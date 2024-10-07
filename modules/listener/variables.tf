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

variable "forwarder_bucket" {
  type        = string
  default     = "axiom-cloudformation"
  description = "name of the S3 bucket where Forwarder Lambda code is stored"
}

variable "forwarder_version" {
  type        = string
  default     = "1.2.0"
  description = "Version of the Axiom CloudWatch Forwarder Lambda"
}
