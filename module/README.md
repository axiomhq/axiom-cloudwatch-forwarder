# terraform-aws-axiom

Setup required infrastructure and install Axiom Enterprise on AWS using Terraform.

## AXiom CloudWatch Forwarder Terraform Module


## Installation

Add the module as a required module in your terraform configuration file.

```hcl
```


```hcl
data "aws_cloudwatch_log_groups" "lambda_groups" {
    # select the log group names to forward logs from
  log_group_name_prefix = "/aws/lambda/"
  }
resource "axiom_dataset" "lambda_forwarder" {
# create a dataset in Axiom
  name = "cloudwatch-lambda"
  description = "[islam] test"
}
module "cloudwatch_lambda_logs_forwarder" {
  source = "https://github.com/axiomhq/axiom-cloudwatch-forwarder-tf.git"
  axiom_dataset = axiom_dataset.lambda_forwarder.name
  axiom_token = "xaat-*"
  prefix = "axiom-cloudwatch"
  log_group_names = data.aws_cloudwatch_log_groups.lambda_groups.log_group_names
}
output "log_group_names" {
  value = module.forwarder.log_group_names
  }
```
