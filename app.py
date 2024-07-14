#!/usr/bin/env python3

# Import necessary libraries
import os
import aws_cdk as cdk

# Import the AxiomStack class from the Axiom module
from Axiom import AxiomStack

# Initialize the CDK application
app = cdk.App()

# Check if the AXIOM_KEY environment variable is set, raise an exception if not
if os.environ.get("AXIOM_KEY") is None:
    raise Exception("AXIOM_KEY environment variable is not set")

# Define AWS account and region where the stack will be deployed
account = "9999999"
region = "us-west-1"
# Create a dataset name using the account number
dataset = "aws-" + account

# Instantiate the AxiomStack with necessary parameters
AxiomStack(app, "AxiomStack",
    axiom_token=os.environ.get("AXIOM_KEY"),  # Axiom API token for authentication
    axiom_url="https://api.axiom.co",  # URL to Axiom API
    axiom_dataset=dataset,  # Dataset name in Axiom
    cloudwatch_log_group_names=[],  # Names of CloudWatch log groups to ingest
    data_tags="",  # Tags to add to the data
    disable_json="false",  # Whether to disable JSON parsing
    cloudwatch_log_groups_prefix="",  # Prefix for CloudWatch log groups
    enable_cloudtrail=False,  # Whether to enable CloudTrail logs ingestion
    log_groups_limit="1000",  # Limit of log groups to ingest
    env=cdk.Environment(account=account, region=region)  # Environment configuration for the CDK app
)

# Synthesize the CDK app, which prepares it for deployment
app.synth()
