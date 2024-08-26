# Axiom CloudWatch Forwarder [![CI](https://github.com/axiomhq/axiom-cloudwatch-forwarder/actions/workflows/ci.yaml/badge.svg)](https://github.com/axiomhq/axiom-cloudwatch-forwarder/actions/workflows/ci.yaml)

Axiom CloudWatch Forwarder is a set of easy-to-use tools designed to forward logs from Amazon CloudWatch to [Axiom](https://axiom.co). It mainly includes a Lambda function to handle the forwarding.

There are two ways to set up the CloudWatch log forwarding:

- [A Terraform module](./module) that sets up the forwarding infrastructure and deploys the Lambda function.
- [Cloudformation Stacks](./cloudformation-stacks) that sets up the forwarding infrastructure and deploys the Lambda function, along with a Subscriber and Listener stacks.
