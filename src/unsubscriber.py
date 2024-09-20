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
    nextToken = resp["nextToken"] if "nextToken" in resp else None
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


def lambda_handler(event: dict, context=None):
    log_group_names = event["ResourceProperties"]["CloudWatchLogGroupNames"]
    log_group_prefix = event["ResourceProperties"]["CloudWatchLogGroupPrefix"]
    log_group_pattern = event["ResourceProperties"]["CloudWatchLogGroupPattern"]

    log_group_names_list = (
        log_group_names.split(",") if log_group_names is not None else []
    )
    log_groups = build_groups_list(
        get_log_groups(), log_group_names_list, log_group_pattern, log_group_prefix
    )

    report = {
        "log_groups_count": len(log_groups),
        "matched_log_groups": [],
        "added_groups": [],
        "added_groups_count": 0,
        "errors": {},
    }

    responseData = {}
    for group in log_groups:
        report["matched_log_groups"].append(group["name"])
        report["errors"][group["name"]] = []

        try:
            delete_subscription_filter(group["name"])
        except Exception as e:
            report["errors"][group["name"]].append(str(e))
            logger.error(
                f"failed to delete subscription filter for {group['name']}, {str(e)}"
            )

        report["added_groups_count"] += 1

        logger.info(
            f"unsubsribed from {report['added_groups_count']} log groups out of {len(report['matched_log_groups'])} groups"
        )

    responseData["success"] = "True"
    cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)
