# Axiom CloudWatch Forwarder [![CI](https://github.com/axiomhq/axiom-cloudwatch-forwarder/actions/workflows/ci.yaml/badge.svg)](https://github.com/axiomhq/axiom-cloudwatch-forwarder/actions/workflows/ci.yaml)

Axiom CloudWatch Lambda is an easy-to-use AWS CloudFormation template to send logs from CloudWatch to [Axiom](https://axiom.co). It deploys a Lambda and a subscriber to create the needed CloudWatch log group subscription filters.

Axiom CloudWatch Lambda uses the following CloudFormation stacks:

- Axiom Forwarder creates a Lambda function that ingests logs from CloudWatch and sends them to Axiom.
- Subscriber runs once to create subscription filters on the ingest Lambda for all existing CloudWatch log groups.
- LogGroups Listener creates a Lambda function that listens for new log groups and creates subscription filters for them. This way, you don't have to create subscription filters manually for new log groups.

## Guide

1. [Create an Axiom account](https://app.axiom.co).
2. Create a dataset in Axiom.
3. Create an API token in Axiom with permissions to ingest data to the dataset you created.
4. [Click this link to launch the Stack](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=axiom-cloudwatch-forwarder&templateURL=https://axiom-cloudformation.s3.amazonaws.com/stacks/axiom-cloudwatch-forwarder-cloudformation-stack.yaml).
5. [Click this link to automatically subscribe to all existing log groups](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=axiom-cloudwatch-subscriber&templateURL=https://axiom-cloudformation.s3.amazonaws.com/stacks/axiom-cloudwatch-subscriber-cloudformation-stack.yaml).
6. [Click this link to automatically subscribe to new log groups](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=axiom-cloudwatch-log-groups-listener&templateURL=https://axiom-cloudformation.s3.amazonaws.com/stacks/axiom-cloudwatch-log-groups-listener-cloudformation-stack.yaml).

## Log Groups Listener architecture

The Log Groups Listener stack does the following:

- It creates an S3 bucket for Cloudtrail.
- It creates a trail to capture the creation of new log groups.
- It creates an event rule to pass those creation events to an EventBridge event bus.
- The EventBridge sends an event to a Lambda function when a new log group is created.
- The Lambda function creates a subscription filter for the new log group.