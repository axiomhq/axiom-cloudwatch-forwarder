# Axiom Cloudwatch Forwarder - Unubscriber

Creates a Lambda function that removes log groups subscriptions from the Forwarder.

## Setup

```hcl
module "unsubscriber" {
  source               = "https://github.com/axiomhq/axiom-cloudwatch-forwarder/tree/main/modules/unsubscriber"
  prefix               = "axiom-cloudwatch-forwarder"
  log_groups_prefix    = "/aws/lambda/"
  forwarder_lambda_arn = module.forwarder.lambda_arn
}
```
