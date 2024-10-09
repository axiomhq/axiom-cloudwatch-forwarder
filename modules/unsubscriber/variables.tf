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

// Which log groups to unsubscribe from?
variable "log_groups_names" {
  type        = string
  description = "A comma separated list of CloudWatch log groups to unsubscribe from"
  default     = ""
}

variable "log_groups_prefix" {
  type        = string
  description = "The Prefix of CloudWatch log groups to unsubscribe from"
  default     = ""
}

variable "log_groups_pattern" {
  type        = string
  description = "A regular expression pattern of CloudWatch log groups to unsubscribe from"
  default     = ""
}


