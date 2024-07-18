# Axiom CloudWatch Forwarder [![CI](https://github.com/axiomhq/axiom-cloudwatch-forwarder/actions/workflows/ci.yaml/badge.svg)](https://github.com/axiomhq/axiom-cloudwatch-forwarder/actions/workflows/ci.yaml)

Axiom CloudWatch Forwarder is a set of easy-to-use AWS CloudFormation stacks designed to forward logs from Amazon CloudWatch to [Axiom](https://axiom.co). It includes a Lambda function to handle the forwarding, as well as subscriber and listener stacks to create CloudWatch log group subscription filters for both existing and future log groups.

Axiom CloudWatch Forwarder includes templates for the following CloudFormation stacks:

- Axiom Forwarder creates a Lambda function that ingests logs from CloudWatch and sends them to Axiom.
- _Subscriber_ runs once to create subscription filters on the _Forwarder_ Lambda for CloudWatch log groups specified by a combination of names, prefix and regular expression.
- LogGroups Listener creates a Lambda function that listens for new log groups and creates subscription filters for them. This way, you don't have to create subscription filters manually for new log groups.

## Guide

1. [Create an Axiom organization](https://app.axiom.co).
2. Create a dataset in Axiom.
3. Create an API token in Axiom with permissions to ingest data to the dataset you created.
4. [Click this link to launch the Forwarder Stack](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=axiom-cloudwatch-forwarder&templateURL=https://axiom-cloudformation.s3.amazonaws.com/stacks/axiom-cloudwatch-forwarder-v1.0.0-cloudformation-stack.yaml).
5. Get the created Forwarder lambda ARN from the previous step, and use it to install the Subscriber stack in the next step.
6. [Click this link to launch the Subscriber stack](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=axiom-cloudwatch-subscriber&templateURL=https://axiom-cloudformation.s3.amazonaws.com/stacks/axiom-cloudwatch-subscriber-v1.0.0-cloudformation-stack.yaml) and automatically subscribe to all existing log groups. You can filter the log groups by one or a combination of names, regex pattern and a prefix.
7. [Click this link to automatically subscribe to new log groups](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=axiom-cloudwatch-log-groups-listener&templateURL=https://axiom-cloudformation.s3.amazonaws.com/stacks/axiom-cloudwatch-log-groups-listener-v1.0.0-cloudformation-stack.yaml).


## Removing subscription filters

If later on, you wanted to remove subscription filters for one or multiple log groups, you can [launch the Unsubscriber stack](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=axiom-cloudwatch-subscriber&templateURL=https://axiom-cloudformation.s3.amazonaws.com/stacks/axiom-cloudwatch-unsubscriber-v1.0.0-cloudformation-stack.yaml)

The log group filtering works the same way as the subscriber stack. You can filter the log groups by one or a combination of names, regex pattern and a prefix.


## Filtering CloudWatch log groups

The Subscriber and Unsubscriber stacks allow you to filter the log groups by one or a combination of names, regex pattern and a prefix. Basically,
You can whitelist a number of log groups. If you don't specify any filter, the stack will subscribe to all log groups. If a log group matches one of the filters, it will be subscribed to.

**Example**

Let's assume we have this list of log groups:

```
/aws/lambda/functionFoo
/aws/lambda/functionBar
/aws/eks/cluster/cluster1
/aws/rds/instanceFoo
```

- To subscribe to the Lambda log groups exclusively, a prefix filter with the value of `/aws/lambda` would do the job.
- To subscribe to eks and rds log groups, a list of names with the value of `/aws/eks/cluster/cluster1,/aws/rds/instanceFoo` would do the job.
- To subscribe to the eks log group and all lambda log groups, a combination of prefix and names list would select them.


## Log Groups Listener architecture

The Log Groups Listener stack does the following:

- It creates an S3 bucket for Cloudtrail.
- It creates a trail to capture the creation of new log groups.
- It creates an event rule to pass those creation events to an EventBridge event bus.
- The EventBridge sends an event to a Lambda function when a new log group is created.
- The Lambda function creates a subscription filter for the new log group.