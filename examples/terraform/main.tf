resource "axiom_dataset" "lambda_forwarder" {
  name        = "cloudwatch-lambda"
  description = "[islam] test"
}

module "forwarder" {
  source        = "../../module/forwarder"
  axiom_dataset = axiom_dataset.lambda_forwarder.name
  axiom_token   = ""
  prefix        = "axiom-cloudwatch-tf-test"
}

module "subscriber" {
  source               = "../../module/subscriber"
  prefix               = "axiom-cloudwatch-tf-test"
  forwarder_lambda_arn = module.forwarder.lambda_arn
  log_groups_prefix    = "/aws/lambda/"
}

output "log_group_names" {
  value = module.subscriber.log_groups_prefix
}
