variable "prefix" {
  type        = string
  default     = "axiom-cloudwatch"
  description = "prefix for resources, defaults to axiom-cloudwatch"
}

// Which log groups to unsubscribe from?
variable "log_groups_names" {
  type        = string
  description = "A comma separated list of CloudWatch log groups to unsubscribe from."
  default     = ""
}

variable "log_groups_prefix" {
  type        = string
  description = "The Prefix of CloudWatch log groups to unsubscribe from."
  default     = ""
}

variable "log_groups_pattern" {
  type        = string
  description = "A regular expression pattern of CloudWatch log groups to unsubscribe from."
  default     = ""
}
