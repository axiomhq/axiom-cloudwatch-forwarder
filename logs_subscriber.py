# subscribe the Axiom ingester to newly created log groups
import boto3
import os
import helpers

# Set environment variables.
axiom_cloudwatch_lambda_ingester_arn = os.getenv("AXIOM_CLOUDWATCH_LAMBDA_INGESTER_ARN")
log_group_prefix = os.getenv("LOG_GROUP_PREFIX", "")

# Set up CloudWatch Logs client.
log_client = boto3.client("logs")


def lambda_handler(event, context):
    """
    Subscribes log ingester to log group from event.

    :param event: Event data from CloudWatch Logs.
    :type event: dict

    :param context: Lambda context object.
    :type context: obj

    :return: None
    """
    # Grab the log group name from incoming event.
    log_group_name = event["detail"]["requestParameters"]["logGroupName"]
  
    # Check whether the prefix is set - the prefix is used to determine which logs we want.
    if not log_group_prefix:
        helpers.create_subscription(
            log_client, log_group_name, axiom_cloudwatch_lambda_ingester_arn, context
        )

        # Check whether the log group's name starts with the set prefix.
    elif log_group_name.startswith(log_group_prefix):
            helpers.create_subscription(
                log_client, log_group_name, axiom_cloudwatch_lambda_ingester_arn, context
            )