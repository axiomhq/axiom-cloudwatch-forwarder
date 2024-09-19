variable "axiom_dataset" {
  type        = string
  description = "Axiom dataset to forward logs to"
}

variable "axiom_token" {
  type        = string
  description = "Axiom token for the dataset"
}

variable "axiom_url" {
  type        = string
  description = "Axiom's API URL"
  default = "https://api.axiom.co"
}

variable "prefix" {
  type        = string
  default     = "axiom-cloudwatch"
  description = "prefix for resources, defaults to axiom-cloudwatch"
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
