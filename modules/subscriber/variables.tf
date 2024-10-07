variable "prefix" {
  type        = string
  default     = "axiom-cloudwatch"
  description = "prefix for resources, defaults to axiom-cloudwatch"
}

variable "forwarder_lambda_arn" {
  type        = string
  description = "The ARN of the Lambda function that forwards logs to Axiom"
}

// Which log groups to subscribe to?
variable "log_groups_names" {
  type        = string
  description = "A comma separated list of CloudWatch log groups to subscribe to."
  default     = ""
}

variable "log_groups_prefix" {
  type        = string
  description = "The Prefix of CloudWatch log groups to subscribe to."
  default     = ""
}

variable "log_groups_pattern" {
  type        = string
  description = "A regular expression pattern of CloudWatch log groups to subscribe to."
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
