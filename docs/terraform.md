# Use Axiom CloudWatch stacks with Terraform

You can use Terraform to deploy Axiom CloudWatch stacks. This guide will show you how to deploy a CloudWatch stack using Terraform.


## Deploying a Forwarder stack


1. Fetch the stack URL from the main Readme.


2. Create a new Terraform file and add the AWS provider:

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~>5.58.0"
    }

    axiom = {
      source = "axiomhq/axiom"
      version = "1.1.2"
    }
  }
}
```

3. Configure Axiom provider and create a dataset and a token:

```hcl
provider "axiom" {
  # Configuration options
  base_url ="https://api.axiom.co"
  api_token = "xaat-****-****"
}

resource "axiom_dataset" "lambda_forwarder" {
  name = "cloudwatch-lambda"
  description = "Lambda logs forwarded from AWS CloudWatch"
}
```

4. Create a CloudFormation stack resource and add the stack URL as a template body:

```hcl
resource "aws_cloudformation_stack" "axiom_cloudwatch_lambda_forwarder" {
  name = "axiom-cloudwatch-lambda-forwarder"

  parameters = {
    AxiomToken = "xaat-****"
    AxiomDataset = axiom_dataset.lambda_forwarder.name
    DataTags = ""
  }

  capabilities = ["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM", "CAPABILITY_AUTO_EXPAND"]

  template_body = file("forwarder_stack_url")
}
```

5. Now, a **Subscriber** is needed to tell the Forwarder which log groups to forward logs from. Create another stack resource to the Terraform file, this time it will have the **Subscriber** stack URL as the template body:

```hcl
resource "aws_cloudformation_stack" "axiom_cloudwatch_lambda_subscriber" {
  name = "axiom-cloudwatch-lambda-subscriber"

  parameters = {
    AxiomCloudWatchForwarderLambdaARN = aws_cloudformation_stack.axiom_cloudwatch_lambda_forwarder.outputs.ForwarderLambdaARN
    CloudWatchLogGroupsNames = ""

    CloudWatchLogGroupsPrefix = "/aws/lambda/"

    CloudWatchLogGroupsPattern = ""
  }

  capabilities = ["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM", "CAPABILITY_AUTO_EXPAND"]

  template_body = file("subscriber-stack-url")
}
```
