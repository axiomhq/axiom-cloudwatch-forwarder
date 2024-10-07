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
  default     = "https://api.axiom.co"
}

variable "prefix" {
  type        = string
  default     = "axiom-cloudwatch"
  description = "prefix for resources, defaults to axiom-cloudwatch"
}

variable "mode" {
  type        = string
  default     = "prod"
  description = "mode for resources, defaults to prod"
}

variable "forwarder_version" {
  type        = string
  default     = "1.2.0"
  description = "Version of the Axiom CloudWatch Forwarder Lambda"
}
