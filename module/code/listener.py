# Automatically subscribes the Axiom CloudWatch Forwarder to newly created log groups
import os
import logging
from helpers import create_subscription_filter

# Set environment variables.
axiom_cloudwatch_forwarder_lambda_arn = os.getenv(
    "AXIOM_CLOUDWATCH_FORWARDER_LAMBDA_ARN"
)
log_group_prefix = os.getenv("LOG_GROUP_PREFIX", "")

# set logger
level = os.getenv("log_level", "INFO")
logging.basicConfig(level=level)
logger = logging.getLogger()
logger.setLevel(level)


def lambda_handler(event, context):
    """
    Subscribes Axiom CloudWatch Forwarder to log group from event.

    :param event: Event data from CloudWatch Logs.
    :type event: dict

    :param context: Lambda context object.
    :type context: obj

    :return: None
    """
    if not "detail" in event:
        return
    # Grab the log group name from incoming event.
    aws_account_id = event["account"]
    aws_region = event["detail"]["awsRegion"]
    log_group_name = event["detail"]["requestParameters"]["logGroupName"]
    log_group_arn = (
        f"arn:aws:logs:{aws_region}:{aws_account_id}:log-group:{log_group_name}:*"
    )

    # Check whether the prefix is set - the prefix is used to determine which logs we want.
    # or whether the log group's name starts with the set prefix.
    if not log_group_prefix or log_group_name.startswith(log_group_prefix):
        create_subscription_filter(
            log_group_arn, axiom_cloudwatch_forwarder_lambda_arn
        )

    else:
        print(
            f"log group ({log_group_name}) did not match the prefix ({log_group_prefix})"
        )
