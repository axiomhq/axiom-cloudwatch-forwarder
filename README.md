# Axiom CloudWatch Forwarder [![CI](https://github.com/axiomhq/axiom-cloudwatch-forwarder/actions/workflows/ci.yaml/badge.svg)](https://github.com/axiomhq/axiom-cloudwatch-forwarder/actions/workflows/ci.yaml)

Axiom CloudWatch Forwarder is a set of easy-to-use AWS CloudFormation stacks designed to forward logs from Amazon CloudWatch to [Axiom](https://axiom.co). It includes a Lambda function to handle the forwarding, as well as stacks to create CloudWatch log group subscription filters for both existing and future log groups.

Axiom CloudWatch Forwarder includes templates for the following CloudFormation stacks:

- **Forwarder** creates a Lambda function that forwards logs from CloudWatch to Axiom.
- **Subscriber** runs once to create subscription filters on _Forwarder_ for CloudWatch log groups specified by a combination of names, prefix, and regular expression.
- **Listener** creates a Lambda function that listens for new log groups and creates subscription filters for them on _Forwarder_. This way, you don't have to create subscription filters manually for new log groups.
- **Unsubscriber**: runs once to remove subscription filters on _Forwarder_ for CloudWatch log groups specified by a combination of names, prefix, and regular expression.

## Setting up CloudWatch log group forwarding

1. Create an Axiom organization at [app.axiom.co](https://app.axiom.co?ref=axiom-cloudwatch-forwarder).
2. Create a dataset in Axiom.
3. Create an API token in Axiom with permissions to ingest data to the dataset you created.
4. [Click this link](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=axiom-cloudwatch-forwarder&templateURL=https://axiom-cloudformation.s3.amazonaws.com/stacks/axiom-cloudwatch-forwarder-v1.1.1-cloudformation-stack.yaml) to open the _Forwarder_ stack template.
5. Copy the _Forwarder_ Lambda ARN from the previous step, as it will be referenced in the _Subscriber_ stack.
6. [Click this link](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=axiom-cloudwatch-subscriber&templateURL=https://axiom-cloudformation.s3.amazonaws.com/stacks/axiom-cloudwatch-subscriber-v1.1.1-cloudformation-stack.yaml) to open the _Subscriber_ stack template.
7. [Click this link](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=axiom-cloudwatch-listener&templateURL=https://axiom-cloudformation.s3.amazonaws.com/stacks/axiom-cloudwatch-listener-v1.1.1-cloudformation-stack.yaml) to open the _Listener_ stack template.

For guidance on unsubscribing from log groups, please see [Removing subscription filters](#Removing-subscription-filters) section below.

## Filtering CloudWatch log groups

The _Subscriber_ and _Unsubscriber_ stacks allow you to filter the log groups by a combination of names, prefix, and regular expression.

If no filters are specified, the stacks will subscribe to or unsubscribe from all log groups. You can also whitelist a specific set of log groups using filters in the CloudFormation stack parameters.

The log group names, prefix, and regular expression filters included are additive, meaning the union of all provided inputs will be matched.

### Example

Assume we have the following list of log groups:

```
/aws/lambda/function-foo
/aws/lambda/function-bar
/aws/eks/cluster/cluster-1
/aws/rds/instance-baz
```

- To subscribe to the Lambda log groups exclusively, a prefix filter with the value of `/aws/lambda` is a good choice.
- To subscribe to EKS and RDS log groups, a list of names with the value of `/aws/eks/cluster/cluster-1,/aws/rds/instance-baz` would work well.
- To subscribe to the EKS log group and all Lambda log groups, a combination of prefix and names list would select them.
- To use the regex filter, you can use a regular expression to match the log group names. For example, `\/aws\/lambda\/.*` would match all Lambda log groups.
- To subscribe to all log groups, leave the filters empty.

## Listener architecture

The optional _Listener_ stack does the following:

- Creates an Amazon S3 bucket for AWS CloudTrail.
- Creates a trail to capture the creation of new log groups.
- Creates an event rule to pass those creation events to an Amazon EventBridge event bus.
- Sends an event via EventBridge to a Lambda function when a new log group is created.
- Creates a subscription filter for each new log group.

## Removing subscription filters

If later on you want to remove subscription filters for one or more log groups:

- [Click this link](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=axiom-cloudwatch-subscriber&templateURL=https://axiom-cloudformation.s3.amazonaws.com/stacks/axiom-cloudwatch-unsubscriber-v1.1.1-cloudformation-stack.yaml) to open the _Unsubscriber_ stack template.

The log group filtering works the same way as the _Subscriber_ stack. You can filter the log groups by a combination of names, prefix and regular expression.
