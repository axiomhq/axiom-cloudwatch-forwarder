import re
from typing import Optional
import boto3
import os
import logging
import cfnresponse

level = os.getenv("log_level", "INFO")
logging.basicConfig(level=level)
logger = logging.getLogger()
logger.setLevel(level)


cloudwatch_logs_client = boto3.client("logs")
lambda_client = boto3.client("lambda")

axiom_cloudwatch_forwarder_lambda_arn = os.getenv(
    "AXIOM_CLOUDWATCH_FORWARDER_LAMBDA_ARN"
)
log_group_names = os.getenv("LOG_GROUP_NAMES", None)
log_group_prefix = os.getenv("LOG_GROUP_PREFIX", None)
log_group_pattern = os.getenv("LOG_GROUP_PATTERN", None)
log_groups_return_limit = 50


def build_groups_list(
    all_groups: list,
    names: Optional[list],
    pattern: Optional[str] = None,
    prefix: Optional[str] = None,
):
    # ensure filter params have correct values
    if not names:
        names = None
    if not pattern:
        pattern = None
    if not prefix:
        prefix = None
    # filter out the log groups based on the names, pattern, and prefix provided in the environment variables
    groups = []
    for g in all_groups:
        group = {"name": g["logGroupName"].strip(), "arn": g["arn"]}
        if names is not None and group["name"] in names:
            groups.append(group)
            continue
        elif prefix is not None and group["name"].startswith(prefix):
            groups.append(group)
            continue
        elif pattern is not None and re.match(pattern, group["name"]):
            groups.append(group)

    return groups


def get_log_groups(nextToken=None):
    # check docs:
    # 1. boto3 https://boto3.amazonaws.com/v1/documentation/api/1.9.42/reference/services/logs.html#CloudWatchLogs.Client.describe_log_groups
    # 2. AWS API https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_DescribeLogGroups.html#API_DescribeLogGroups_RequestSyntax
    resp = cloudwatch_logs_client.describe_log_groups(limit=log_groups_return_limit)
    all_groups = resp["logGroups"]
    nextToken = resp["nextToken"]
    # continue fetching log groups until nextToken is None
    while nextToken is not None:
        resp = cloudwatch_logs_client.describe_log_groups(
            limit=log_groups_return_limit, nextToken=nextToken
        )
        all_groups.extend(resp["logGroups"])
        nextToken = resp["nextToken"] if "nextToken" in resp else None

    return all_groups


def delete_subscription_filter(log_group_name: str):
    logger.info(f"Deleting subscription filter for {log_group_name}...")

    cloudwatch_logs_client.delete_subscription_filter(
        logGroupName=log_group_name, filterName="%s-axiom" % log_group_name
    )

    logger.info(f"{log_group_name} subscription filter has been deleted successfully.")


def remove_permission(statement_id: str, lambda_arn: str):
    lambda_client.remove_permission(
        FunctionName=lambda_arn,
        StatementId=statement_id,
    )


def lambda_handler(event: dict, context=None):
    if (
        axiom_cloudwatch_forwarder_lambda_arn is None
        or axiom_cloudwatch_forwarder_lambda_arn == ""
    ):
        responseData = {
            "success": False,
            "body": "AXIOM_CLOUDWATCH_LAMBDA_FORWARDER_ARN is not set",
        }
        cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)
        return

    forwarder_lambda_group_name = (
        "/aws/lambda/" + axiom_cloudwatch_forwarder_lambda_arn.split(":")[-1]
    )

    log_group_names_list = (
        log_group_names.split(",") if log_group_names is not None else []
    )
    log_groups = build_groups_list(
        get_log_groups(), log_group_names_list, log_group_pattern, log_group_prefix
    )

    responseData = {}
    try:
        for group in log_groups:
            # skip the Forwarder lambda log group to avoid circular logging
            if group["name"] == forwarder_lambda_group_name:
                continue

            try:
                delete_subscription_filter(group["name"])
            except Exception as e:
                logger.error(
                    f"failed to delete subscription filter for {group['name']}, {str(e)}"
                )
                pass

            # remove the permission from the lambda
            cleaned_name = "-".join(group["name"].split("/")[3:])
            statement_id = f"invoke-permission-for-{cleaned_name}"
            try:
                remove_permission(statement_id, axiom_cloudwatch_forwarder_lambda_arn)
            except Exception as e:
                logger.warning(
                    f"failed to remove permission for {cleaned_name}: {str(e)}"
                )

    except Exception as e:
        responseData["success"] = "False"
        responseData["body"] = str(e)
        cfnresponse.send(event, context, cfnresponse.FAILED, responseData)
        return

    responseData["success"] = "True"
    cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)
