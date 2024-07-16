# Axiom CloudWatch Lambda [![CI](https://github.com/axiomhq/axiom-cloudwatch-lambda/actions/workflows/ci.yaml/badge.svg)](https://github.com/axiomhq/axiom-cloudwatch-lambda/actions/workflows/ci.yaml)

Axiom CloudWatch Lambda is an easy-to-use AWS CloudFormation template to send logs from CloudWatch to [Axiom](https://axiom.co). It deploys a CloudWatch log group subscription filter and a Lambda.

Axiom CloudWatch Lambda uses the following CloudFormation stacks:

- Axiom Ingester creates a Lambda function that ingests logs from CloudWatch and sends them to Axiom.
- Backfiller runs once to create subscription filters on the ingest Lambda for all existing CloudWatch log groups.
- Logs Subscriber creates a Lambda function that listens for new log groups and creates subscription filters for them. This way, you don't have to create subscription filters manually for new log groups.

## Guide

1. [Create an Axiom account](https://app.axiom.co).
2. Create a dataset in Axiom.
3. Create an API token in Axiom with permissions to ingest data to the dataset you created.
4. [Click this link to launch the Stack](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=cloudwatch-ingester-axiom&templateURL=https://axiom-cloudformation.s3.amazonaws.com/stacks/axiom-cloudwatch-ingester-cloudformation-stack.yaml).
5. [Click this link to automatically subscribe to all existing log groups](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=cloudwatch-backfiller-axiom&templateURL=https://axiom-cloudformation.s3.amazonaws.com/stacks/axiom-cloudwatch-backfiller-cloudformation-stack.yaml).
6. [Click this link to automatically subscribe to new log groups](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=cloudwatch-subscriber-axiom&templateURL=https://axiom-cloudformation.s3.amazonaws.com/stacks/axiom-cloudwatch-subscriber-cloudformation-stack.yaml).

## Logs Subscriber architecture

The Logs Subscriber stack does the following:

- It creates an S3 bucket for Cloudtrail.
- It creates a trail to capture the creation of new log groups.
- It creates an event rule to pass those creation events to an EventBridge event bus.
- The EventBridge sends an event to a Lambda function when a new log group is created.
- The Lambda function creates a subscription filter for the new log group.