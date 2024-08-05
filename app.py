#!/usr/bin/env python3

# Import necessary libraries
import os
import aws_cdk as cdk

# Import the AxiomStack class from the Axiom module
from Axiom import AxiomCloudWatchStack

# Initialize the CDK application
app = cdk.App()

# Check if the AXIOM_KEY environment variable is set, raise an exception if not
if os.environ.get("AXIOM_TOKEN") is None:
    raise Exception("AXIOM_TOKEN environment variable is not set")

# Define AWS account and region where the stack will be deployed
account = os.environ.get("CDK_DEFAULT_ACCOUNT")
region = os.environ.get("CDK_DEFAULT_REGION")
# Create a dataset name using the account number
#
if account is None:
    raise Exception("CDK_DEFAULT_ACCOUNT environment variable is not set")
if region is None:
    raise Exception("CDK_DEFAULT_REGION environment variable is not set")
dataset = os.environ.get("AXIOM_DATASET") or "aws-" + account

# Instantiate the AxiomCloudWatchStack with necessary parameters
AxiomCloudWatchStack(
    app,
    "AxiomCloudWatchForwarder",
    axiom_token=os.environ.get("AXIOM_TOKEN"),  # Axiom API token for authentication
    axiom_url="https://api.dev.axiomtestlabs.co",  # URL to Axiom API
    axiom_dataset=dataset,  # Dataset name in Axiom
    data_tags="",  # Tags to add to the data
    cloudwatch_log_groups_names=[],  # Names of CloudWatch log groups to ingest
    cloudwatch_log_groups_prefix="/aws/lambda/",  # Prefix for CloudWatch log groups
    cloudwatch_log_groups_pattern="",  # Prefix for CloudWatch log groups
    enable_cloudtrail=False,  # Whether to enable CloudTrail logs ingestion
    env=cdk.Environment(
        account=account, region=region
    ),  # Environment configuration for the CDK app
)

# Synthesize the CDK app, which prepares it for deployment
app.synth()
