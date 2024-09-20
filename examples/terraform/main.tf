resource "axiom_dataset" "lambda_forwarder" {
  name        = "cloudwatch-lambda"
  description = "[islam] test"
}

module "forwarder" {
  source            = "../../module"
  axiom_dataset     = axiom_dataset.lambda_forwarder.name
  axiom_token       = ""
  prefix            = "axiom-cloudwatch-tf-test"
  log_groups_prefix = "/aws/lambda/"
}


output "log_group_names" {
  value = module.forwarder.log_groups_prefix
}
