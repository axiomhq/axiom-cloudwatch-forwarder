import os
import re
import logging
from typing import Optional
from helpers import send_response, build_groups_list, get_log_groups, delete_subscription_filter


level = os.getenv("log_level", "INFO")
logging.basicConfig(level=level)
logger = logging.getLogger()
logger.setLevel(level)


def lambda_handler(event: dict, context=None):
    log_group_names = event['CloudWatchLogGroupNames']
    log_group_prefix = event['CloudWatchLogGroupPrefix']
    log_group_pattern = event['CloudWatchLogGroupPattern']

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
    send_response(event, context, "SUCCESS", responseData)
