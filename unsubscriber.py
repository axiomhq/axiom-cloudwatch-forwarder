import re
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
log_group_names = os.getenv("LOG_GROUP_NAMES", "")
log_group_prefix = os.getenv("LOG_GROUP_PREFIX", "")
log_group_pattern = os.getenv("LOG_GROUP_PATTERN", "")


def build_groups_list(all_groups, names, pattern, prefix):
    # filter out the log groups based on the names, pattern, and prefix provided in the environment variables
    groups = []
    for g in all_groups:
        group = {"name": g["logGroupName"], "arn": g["arn"]}
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
        # print(f'got ${len(all_groups)} groups')
        nextToken = resp["nextToken"] if "nextToken" in resp else None

    return all_groups


def delete_subscription_filter(log_group_arn):
    try:
        log_group_name = log_group_arn.split(":")[-2]

        logger.info(f"Deleting subscription filter for {log_group_name}...")

        cloudwatch_logs_client.delete_subscription_filter(
            logGroupName=log_group_name, filterName="%s-axiom" % log_group_name
        )

        logger.info(
            f"{log_group_name} subscription filter has been deleted successfully."
        )

    except Exception as e:
        logger.error(f"Error deleting Subscription filter: {e}")
        raise e


def lambda_handler(event: dict, context=None):
    if axiom_cloudwatch_forwarder_lambda_arn is None:
        raise Exception("AXIOM_CLOUDWATCH_LAMBDA_FORWARDER_ARN is not set")

    aws_account_id = context.invoked_function_arn.split(":")[4]
    region = os.getenv("AWS_REGION")

    forwarder_lambda_group_name = (
        "/aws/lambda/" + axiom_cloudwatch_forwarder_lambda_arn.split(":")[-1]
    )

    log_groups = build_groups_list(
        get_log_groups(), log_group_names, log_group_pattern, log_group_prefix
    )

    responseData = {}
    try:
        for group in log_groups:
            # skip the Forwarder lambda log group to avoid circular logging
            if group["logGroupName"] == forwarder_lambda_group_name:
                continue

            try:
                delete_subscription_filter(
                    region, aws_account_id, axiom_cloudwatch_forwarder_lambda_arn
                )
            except Exception:
                pass
    except Exception as e:
        responseData["success"] = "False"
        if "ResponseURL" in event:
            cfnresponse.send(event, context, cfnresponse.FAILED, responseData)
        else:
            raise e

    responseData["success"] = "True"
    if "ResponseURL" in event:
        cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)
    else:
        return "ok"
