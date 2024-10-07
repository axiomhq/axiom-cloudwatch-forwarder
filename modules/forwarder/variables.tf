variable "prefix" {
  type        = string
  description = "Prefix for resources, defaults to axiom-cloudwatch"
  default     = "axiom-cloudwatch"
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

