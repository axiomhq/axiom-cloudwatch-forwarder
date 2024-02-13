# Axiom CloudWatch Lambda [![CI](https://github.com/axiomhq/axiom-cloudwatch-lambda/actions/workflows/ci.yaml/badge.svg)](https://github.com/axiomhq/axiom-cloudwatch-lambda/actions/workflows/ci.yaml)

Easy to use AWS CloudFormation template to deploy a CloudWatch Log Group subscription filter and A lambda to push the
logs from your CloudWatch to [Axiom](https://axiom.co).

## Guide

1. Create an account at [Axiom Cloud](https://cloud.axiom.co)
2. Create a dataset and an API token with ingest permission for that dataset
3. Launch the stack: [![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=CloudWatch-Axiom&templateURL=https://axiom-cloudformation-stacks.s3.amazonaws.com/axiom-cloudwatch-lambda-cloudformation-stack.yaml)
4. Subscribe to more LogGroups: [![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=CloudWatch-Backfiller-Axiom&templateURL=https://axiom-cloudformation-stacks.s3.amazonaws.com/axiom-cloudwatch-backfiller-lambda-cloudformation-stack.yaml)
5. Automatically Subscribe to new LogGroups: [![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=Axiom-CloudWatch-LogsSubscriber&templateURL=https://axiom-cloudformation-stacks.s3.amazonaws.com/axiom-cloudwatch-logs-subscriber-cloudformation-stack.yaml)


# Logs Subscriber architecture

- Creates a CloudTrail trail to capture creation of new LogGroups
- 
- EventBridge sends an event to a Lambda function when a new LogGroup is created
- Lambda function creates a subscription filter for the new LogGroup