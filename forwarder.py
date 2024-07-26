import re
import os
import base64
import gzip
import json
import boto3
import logging
import urllib.request
import cfnresponse

level = os.getenv("log_level", "INFO")
logging.basicConfig(level=level)
logger = logging.getLogger()
logger.setLevel(level)

cloudwatch_logs_client = boto3.client("logs")

# Standard out from Lambdas.
std_matcher = re.compile(r"\d\d\d\d-\d\d-\d\d\S+\s+(?P<requestID>\S+)")

# END RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
end_matcher = re.compile(r"END RequestId:\s+(?P<requestID>\S+)")

# START RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
# Version: $LATEST
start_matcher = re.compile(
    r"START RequestId:\s+(?P<requestID>\S+)\s+" "Version: (?P<version>\S+)"
)

# REPORT RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
# Duration: 0.47 ms
# Billed Duration: 100 ms
# Memory Size: 128 MB
# Max Memory Used: 20 MB
report_matcher = re.compile(
    "REPORT RequestId:\s+(?P<requestID>\S+)\s+"
    "Duration: (?P<durationMS>\S+) ms\s+"
    "Billed Duration: (?P<billedDurationMS>\S+) ms\s+"
    "Memory Size: (?P<memorySizeMB>\S+) MB\s+"
    "Max Memory Used: (?P<maxMemoryMB>\S+) MB"
)


# push events to axiom
axiom_url = os.getenv("AXIOM_URL", "https://api.axiom.co").strip("/")
axiom_token = os.getenv("AXIOM_TOKEN")
axiom_dataset = os.getenv("AXIOM_DATASET")
data_tags_string = os.getenv("DATA_TAGS")
data_service_name = os.getenv("DATA_MESSAGE_KEY")

data_tags = {}
if data_tags_string != "":
    data_tags_list = data_tags_string.split(",")
    for tag in data_tags_list:
        tag_splitted = tag.strip(" ").split("=")
        if len(tag_splitted) != 2:
            continue
        data_tags[tag_splitted[0]] = tag_splitted[1]


# try to get json from message
def structured_message(message: str):
    try:
        return json.loads(message)
    except:
        return None


def push_events_to_axiom(events: list):
    if len(events) == 0:
        return

    url = f"{axiom_url}/v1/datasets/{axiom_dataset}/ingest"
    data = json.dumps(events)
    req = urllib.request.Request(
        url,
        data=bytes(data, "utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {axiom_token}",
        },
    )

    result = urllib.request.urlopen(req)
    if result.status != 200:
        raise f"Unexpected status {result.status}"
    else:
        logger.info(f"Successfully pushed {len(events)} events to axiom")


def data_from_event(event: dict) -> dict:
    if "awslogs" not in event or "data" not in event["awslogs"]:
        logger.warning(f"Unexpected event format: {json.dumps(event)}")
        return {}

    body = base64.b64decode(event["awslogs"]["data"])
    data = gzip.decompress(body)
    return json.loads(data)


def parse_message(message):
    m = None

    # Determine which matcher to use depending on the message type.
    if message.startswith("REPORT"):
        m = report_matcher.match(message)
        m = m.groupdict()
        # convert from string to number
        m["durationMS"] = float(m["durationMS"])
        m["billedDurationMS"] = int(m["billedDurationMS"])
        m["memorySizeMB"] = int(m["memorySizeMB"])
        m["maxMemoryMB"] = int(m["maxMemoryMB"])
        return m
    elif message.startswith("END"):
        m = end_matcher.match(message)
    elif message.startswith("START"):
        m = start_matcher.match(message)
    else:
        m = std_matcher.match(message)

    return {} if m is None else m.groupdict()


def split_log_group(log_group: str):
    # this is an extra field, we can extend this without a problem
    pattern_obj = re.compile("^/aws/(lambda|apigateway|eks|rds)/(.*)")
    parsed = pattern_obj.match(log_group)
    if parsed is None:
        return {
            "serviceName": (
                data_service_name if data_service_name is not None else "unknown"
            ),
            "logGroupName": log_group,
        }

    service_name = (
        data_service_name if data_service_name is not None else parsed.group(1)
    )
    log_group_name = parsed.group(2)

    return {
        "serviceName": service_name if service_name is not None else "unknown",
        "logGroupName": log_group_name if log_group_name is not None else "",
    }


def get_log_groups(nextToken=None):
    # check docs:
    # 1. boto3 https://boto3.amazonaws.com/v1/documentation/api/1.9.42/reference/services/logs.html#CloudWatchLogs.Client.describe_log_groups
    # 2. AWS API https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_DescribeLogGroups.html#API_DescribeLogGroups_RequestSyntax
    resp = cloudwatch_logs_client.describe_log_groups(limit=50)
    all_groups = resp["logGroups"]
    nextToken = resp["nextToken"]
    # continue fetching log groups until nextToken is None
    while nextToken is not None:
        resp = cloudwatch_logs_client.describe_log_groups(limit=50, nextToken=nextToken)
        all_groups.extend(resp["logGroups"])
        nextToken = resp["nextToken"] if "nextToken" in resp else None

    return all_groups


def lambda_handler(event: dict, context=None):
    # handle deletion of the stack
    if "RequestType" in event and event["RequestType"] == "Delete":
        # remove all related subscription filters, unforutunately deleting the lambda will
        # not clear the subscription filters
        # We can do so by looping over log groups and deleting the subscription filters
        # 1. get lambda arn
        fn_name = os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
        lambda_client = boto3.client("lambda")
        response = lambda_client.get_function_configuration(FunctionName=fn_name)
        # 2. get log groups
        log_groups = get_log_groups()
        for group in log_groups:
            # 3. get subscription filters
            filters = cloudwatch_logs_client.describe_subscription_filters(
                logGroupName=group["logGroupName"]
            )
            for filter in filters["subscriptionFilters"]:
                # 4. check if filter is related to the lambda
                if filter["destinationArn"] == response["FunctionArn"]:
                    # 5. delete subscription filter
                    cloudwatch_logs_client.delete_subscription_filter(
                        logGroupName=group["logGroupName"],
                        filterName=filter["filterName"],
                    )
        cfnresponse.send(
            event, context, cfnresponse.SUCCESS, {}, event["PhysicalResourceId"]
        )
        return

    if axiom_token is None:
        raise Exception("AXIOM_TOKEN is not set")
    if axiom_dataset is None:
        raise Exception("AXIOM_DATASET is not set")

    data = data_from_event(event)
    if not data:
        return

    aws_fields = {
        "owner": data.get("owner"),
        "logGroup": data.get("logGroup"),
        "logStream": data.get("logStream"),
        "messageType": data.get("messageType"),
        "subscriptionFilters": data.get("subscriptionFilters"),
        "serviceName": "unknown",
        "logGroupName": "",
    }

    if len(data_tags) > 0:
        aws_fields.update({"tags": data_tags})

    # parse the loggroup to get the service and function
    if aws_fields["logGroup"] is not None:
        # add the service and function to the fields
        extra = split_log_group(aws_fields["logGroup"])
        aws_fields.update(extra)

    events = []
    for log_event in data["logEvents"]:
        message = log_event["message"]
        ev = {
            "_time": log_event["timestamp"] * 1000,
            "aws": aws_fields,
            "message": message,
        }

        lambda_data = None
        json_data = None
        if message.startswith("{") and message.endswith("}"):
            # Try to Parse message as JSON
            json_data = structured_message(message)
            if json_data is not None:
                # Data is parsed to JSON, so use it
                lambda_data = json_data

        # Message is not JSON or parsing failed.
        if json_data is None:
            msg = parse_message(message)
            if len(msg) != 0:
                lambda_data = msg

        if lambda_data is not None:
            if "serviceName" in aws_fields:
                ev.update({aws_fields["serviceName"]: lambda_data})

        events.append(ev)

    try:
        push_events_to_axiom(events)
    except Exception as e:
        logger.error(f"Error pushing events to axiom: {e}")
        raise e
