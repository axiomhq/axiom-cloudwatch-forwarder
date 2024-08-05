import re
import boto3
import os
import logging
from typing import Optional
from common import send_response, fetch_log_groups, build_groups_list

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


def delete_subscription_filter(log_group_name: str):
    logger.info(f"Deleting subscription filter for {log_group_name}...")

    cloudwatch_logs_client.delete_subscription_filter(
        logGroupName=log_group_name, filterName="%s-axiom" % log_group_name
    )

    logger.info(f"{log_group_name} subscription filter has been deleted successfully.")


def lambda_handler(event: dict, context=None):
    if (
        axiom_cloudwatch_forwarder_lambda_arn is None
        or axiom_cloudwatch_forwarder_lambda_arn == ""
    ):
        responseData = {
            "success": False,
            "body": "AXIOM_CLOUDWATCH_LAMBDA_FORWARDER_ARN is not set",
        }
        send_response(event, context, "SUCCESS", responseData)
        return

    forwarder_lambda_group_name = (
        "/aws/lambda/" + axiom_cloudwatch_forwarder_lambda_arn.split(":")[-1]
    )

    log_group_names_list = (
        log_group_names.split(",") if log_group_names is not None else []
    )
    log_groups = build_groups_list(
        fetch_log_groups(cloudwatch_logs_client), log_group_names_list, log_group_pattern, log_group_prefix
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
        # skip the Forwarder lambda log group to avoid circular logging
        if group["name"] == forwarder_lambda_group_name:
            continue

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
    send_response(event, context, "SUCCESS", responseData)
