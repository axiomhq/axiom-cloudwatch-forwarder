import re
import boto3
import os
import logging
import cfnresponse
from typing import Optional

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
    names: Optional[list] = None,
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
        if names is None and pattern is None and prefix is None:
            groups.append(group)
            continue
        elif names is not None and group["name"] in names:
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


def create_subscription_filter(log_group_arn: str, lambda_arn: str):
    log_group_name = log_group_arn.split(":")[-2]
    logger.info(f"Creating subscription filter for {log_group_name}")

    filter_name = "%s-axiom" % log_group_name

    cloudwatch_logs_client.put_subscription_filter(
        logGroupName=log_group_name,
        filterName=filter_name,
        filterPattern="",
        destinationArn=lambda_arn,
        distribution="ByLogStream",
    )
    logger.info(f"{log_group_name} subscription filter has been created successfully.")


def lambda_handler(event: dict, context=None):
    # handle deletion of the stack
    if event["RequestType"] == "Delete":
        cfnresponse.send(
            event, context, cfnresponse.SUCCESS, {}, event["PhysicalResourceId"]
        )
        return

    if (
        axiom_cloudwatch_forwarder_lambda_arn is None
        or axiom_cloudwatch_forwarder_lambda_arn == ""
    ):
        raise Exception("AXIOM_CLOUDWATCH_LAMBDA_FORWARDER_ARN is not set")

    aws_account_id = context.invoked_function_arn.split(":")[4]
    region = os.getenv("AWS_REGION")

    log_group_names_list = (
        log_group_names.split(",") if log_group_names is not None else []
    )
    log_groups = build_groups_list(
        get_log_groups(), log_group_names_list, log_group_pattern, log_group_prefix
    )

    # report number of log groups found
    logger.info(f"Found {len(log_groups)} log groups that matches the criteria.")

    report = {
        "log_groups_count": len(log_groups),
        "matched_log_groups": [],
        "added_groups": [],
        "added_groups_count": 0,
        "errors": {},
    }
    for group in log_groups:
        # skip the Forwarder lambda log group to avoid circular logging
        if group["name"].startswith("/aws/axiom/"):
            continue

        # create invoke permission for lambda
        cleaned_name = "-".join(group["name"].split("/")[3:])

        report["matched_log_groups"].append(group["name"])
        report["errors"][group["name"]] = []

        try:
            create_subscription_filter(
                group["arn"], axiom_cloudwatch_forwarder_lambda_arn
            )
            report["added_groups_count"] += 1
            report["added_groups"].append(group["name"])
        except cloudwatch_logs_client.exceptions.LimitExceededException as error:
            report["errors"][group["name"]].append(str(error))
            logger.error(
                "failed to create subscription filter for: %s. Cannot create more log groups. Create another Forwarder with different log groups configuration."
                % group["name"]
            )
            logger.error(error)
            break
        except Exception as error:
            report["errors"][group["name"]].append(str(error))
            logger.error("failed to create subscription filter for: %s" % group["name"])
            logger.error(error)
            continue

    logger.info(
        f"created subscription for {report['added_groups_count']} log groups out of {len(report['matched_log_groups'])} groups"
    )
    logger.info(report)
    responseData = {"success": True}
    cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)
