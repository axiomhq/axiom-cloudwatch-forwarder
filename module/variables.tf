variable "axiom_dataset" {
  type        = string
  description = "Axiom dataset to forward logs to"
}

variable "axiom_token" {
  type        = string
  description = "Axiom token for the dataset"
}

variable "prefix" {
  type        = string
  default     = "axiom-cloudwatch"
  description = "prefix for resources, defaults to axiom-cloudwatch"
}


variable "log_group_names" {
  type        = list(string)
  description = "list of log group names to forward to Axiom"
}
