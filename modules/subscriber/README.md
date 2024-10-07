# Axiom Cloudwatch Forwarder - Subscriber

Creates a Lambda function that subscribers the Forwarder to AWS Cloudwatch log groups.

## Setup

```hcl
module "subscriber" {
  source               = "https://github.com/axiomhq/axiom-cloudwatch-forwarder/tree/main/modules/subscriber"
  prefix               = "axiom-cloudwatch-forwarder"
  axiom_dataset        = "DATASET_NAME"
  log_groups_prefix    = "/aws/lambda/"
  forwarder_lambda_arn = module.forwarder.lambda_arn
}
```
