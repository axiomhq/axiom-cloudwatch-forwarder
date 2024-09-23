import os
import logging
from typing import TypedDict
from .helpers import (
    send_response,
    build_groups_list,
    get_log_groups,
    create_subscription_filter,
    cloudwatch_logs_client,
)

level = os.getenv("log_level", "INFO")
logging.basicConfig(level=level)
logger = logging.getLogger()
logger.setLevel(level)

axiom_cloudwatch_forwarder_lambda_arn = os.getenv(
    "AXIOM_CLOUDWATCH_FORWARDER_LAMBDA_ARN"
)


def is_delete_event(invoke_source: str, event: dict) -> bool:
    if invoke_source == "cloudformation" and event["RequestType"] == "Delete":
        return True
    elif invoke_source == "terraform" and event["tf"]["action"] == "delete":
        return True
    else:
        return False


def get_log_group_config(invoke_source: str, event: dict):
    Config = TypedDict(
        "Config",
        {
            "log_group_names": str,
            "log_group_prefix": str,
            "log_group_pattern": str,
        },
    )
    config: Config = {
        "log_group_names": "",
        "log_group_prefix": "",
        "log_group_pattern": "",
    }
    if invoke_source == "cloudformation":
        config["log_group_names"] = event["ResourceProperties"][
            "CloudWatchLogGroupNames"
        ]
        config["log_group_prefix"] = event["ResourceProperties"][
            "CloudWatchLogGroupPrefix"
        ]
        config["log_group_pattern"] = event["ResourceProperties"][
            "CloudWatchLogGroupPattern"
        ]
    elif invoke_source == "terraform":
        config["log_group_names"] = event["CloudWatchLogGroupNames"]
        config["log_group_prefix"] = event["CloudWatchLogGroupPrefix"]
        config["log_group_pattern"] = event["CloudWatchLogGroupPattern"]

    return config


def lambda_handler(event: dict, context):
    # detect the source of the invocation
    invoke_source = None
    if "tf" in event:
        invoke_source = "terraform"
    elif "ResourceProperties" in event:
        invoke_source = "cloudformation"
    else:
        raise Exception("Unknown source of invocation")

    # TODO: Handle delete event
    if is_delete_event(invoke_source, event):
        send_response(event, context, "SUCCESS", {})
        return

    # extract the log group names, prefix and pattern from the event
    config = get_log_group_config(invoke_source, event)
    log_group_names = config.get("log_group_names")
    log_group_prefix = config.get("log_group_prefix")
    log_group_pattern = config.get("log_group_pattern")

    if (
        axiom_cloudwatch_forwarder_lambda_arn is None
        or axiom_cloudwatch_forwarder_lambda_arn == ""
    ):
        raise Exception("AXIOM_CLOUDWATCH_LAMBDA_FORWARDER_ARN is not set")

    log_group_names_list = (
        log_group_names.split(",") if log_group_names is not None else []
    )
    log_groups = build_groups_list(
        get_log_groups(), log_group_names_list, log_group_pattern, log_group_prefix
    )

    # report number of log groups found
    logger.info(f"Found {len(log_groups)} log groups that matches the criteria.")

    Report = TypedDict(
        "Report",
        {
            "log_groups_count": int,
            "matched_log_groups": list,
            "added_groups": list,
            "added_groups_count": int,
            "errors": dict,
        },
    )
    report: Report = {
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
    send_response(event, context, "SUCCESS", responseData)
