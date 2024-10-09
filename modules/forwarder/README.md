# Axiom Cloudwatch Forwarder

Forward logs from AWS Cloudwatch to Axiom.

## Setup

```hcl
module "forwarder" {
  source        = "https://github.com/axiomhq/axiom-cloudwatch-forwarder/tree/main/modules/forwarder"
  prefix        = "axiom-cloudwatch-forwarder"
  axiom_dataset = "DATASET_NAME"
  axiom_token   = "xaat-***"
}
```
