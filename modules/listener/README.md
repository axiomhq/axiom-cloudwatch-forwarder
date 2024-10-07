# Axiom Cloudwatch Forwarder - Listener

This module sets up a lambda function that listens to Cloudwatch logs and subscribers the Axiom's Forwarder to these groups.

## Setup

```hcl
module "listener" {
  source               = "https://github.com/axiomhq/axiom-cloudwatch-forwarder/tree/main/modules/listener"
  prefix               = "axiom-cloudwatch-forwarder"
  forwarder_lambda_arn = module.forwarder.lambda_arn
  log_groups_prefix    = "/aws/lambda/"
}
```
