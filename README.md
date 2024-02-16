# Axiom CloudWatch Lambda [![CI](https://github.com/axiomhq/axiom-cloudwatch-lambda/actions/workflows/ci.yaml/badge.svg)](https://github.com/axiomhq/axiom-cloudwatch-lambda/actions/workflows/ci.yaml)

Easy to use AWS CloudFormation template to deploy a CloudWatch Log Group subscription filter and a Lambda to push the
logs from your CloudWatch to [Axiom](https://axiom.co).


Axiom’s CloudWatch Lambda is deployed using three distinct CloudFormation stacks. These stacks are responsible for the following:

1. Axiom Ingester: This stack creates a Lambda function that ingests logs from CloudWatch and sends them to Axiom.
2. Backfiller: This stack runs once to create subscription filters on the ingest Lambda,  for all existing CloudWatch log groups.
3. LogsSubscriber: This stack creates a Lambda function that listens for new log groups and creates subscription filters for them. This way you don't have to create subscription filters manually for new log groups.

## Guide

1. Create an account at [Axiom](https://app.axiom.co)
2. Create a dataset and an API token with ingest permission for that dataset
3. Launch the stack: [![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=CloudWatch-Axiom&templateURL=https://axiom-cloudformation-stacks.s3.amazonaws.com/axiom-cloudwatch-lambda-cloudformation-stack.yaml)
4. Automatically subscribe to all existing log groups: [![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=CloudWatch-Backfiller-Axiom&templateURL=https://axiom-cloudformation-stacks.s3.amazonaws.com/axiom-cloudwatch-backfiller-lambda-cloudformation-stack.yaml)
5. Automatically Subscribe to new log groups: [![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=Axiom-CloudWatch-LogsSubscriber&templateURL=https://axiom-cloudformation-stacks.s3.amazonaws.com/axiom-cloudwatch-logs-subscriber-cloudformation-stack.yaml)


# Logs Subscriber architecture

- Creates an S3 bucket for Cloudtrail
- Creates a Trail to capture creation of new log groups
- Creates an Event Rule to pass those creation events to event bus
- EventBridge sends an event to a Lambda function when a new log group is created
- Lambda function creates a subscription filter for the new log group
