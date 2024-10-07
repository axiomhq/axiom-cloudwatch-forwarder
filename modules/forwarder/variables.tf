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

variable "lambda_zip_bucket" {
  type        = string
  default     = "axiom-cloudformation"
  description = "Name of the S3 bucket where Lambda code is stored"
}

variable "lambda_zip_version" {
  type        = string
  default     = "1.2.0"
  description = "Version of the Axiom Lambda"
}
