data "aws_cloudwatch_log_groups" "lambda_groups" {
  log_group_name_prefix = "/aws/lambda/"
}

resource "axiom_dataset" "lambda_forwarder" {
  name        = "cloudwatch-lambda"
  description = "[islam] test"
}

module "forwarder" {
  source          = "../../module"
  axiom_dataset   = axiom_dataset.lambda_forwarder.name
  axiom_token     = "xaat-46c6366c-47fe-487d-95fc-f35af3b55d20"
  prefix          = "axiom-cloudwatch-tf-test"
  log_group_names = data.aws_cloudwatch_log_groups.lambda_groups.log_group_names
}


output "log_group_names" {
  value = module.forwarder.log_group_names
}
