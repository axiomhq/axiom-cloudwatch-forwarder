import base64
import gzip
import json
import logging
import os
import re
import urllib.request

level = os.getenv("log_level", "INFO")
logging.basicConfig(level=level)
logger = logging.getLogger()
logger.setLevel(level)


# Standard out from Lambdas.
std_matcher = re.compile("\d\d\d\d-\d\d-\d\d\S+\s+(?P<requestID>\S+)")

# END RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
end_matcher = re.compile("END RequestId:\s+(?P<requestID>\S+)")

# START RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
# Version: $LATEST
start_matcher = re.compile(
    "START RequestId:\s+(?P<requestID>\S+)\s+" "Version: (?P<version>\S+)"
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
axiom_url = os.getenv("AXIOM_URL", "https://cloud.axiom.co")
axiom_token = os.getenv("AXIOM_TOKEN")
axiom_dataset = os.getenv("AXIOM_DATASET")

# try to get json from message
def structured_message(message: str):
    try:
        return json.loads(message)
    except:
        return None


def push_events_to_axiom(events: list):
    if len(events) == 0:
        return

    url = f"{axiom_url}/api/v1/datasets/{axiom_dataset}/ingest"
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
        return {}

    service_name = parsed.group(1)
    log_group_name = parsed.group(2)

    return {
        "serviceName": service_name if service_name is not None else "unknown",
        "logGroupName": log_group_name if log_group_name is not None else "",
    }


def lambda_handler(event: dict, context=None):
    if axiom_token is None:
        raise Exception("AXIOM_TOKEN is not set")
    if axiom_dataset is None:
        raise Exception("AXIOM_DATASET is not set")

    data = data_from_event(event)

    aws_fields = {
        "owner": data.get("owner"),
        "logGroup": data.get("logGroup"),
        "logStream": data.get("logStream"),
        "messageType": data.get("messageType"),
        "subscriptionFilters": data.get("subscriptionFilters"),
    }

    # parse the loggroup to get the service and function
    if aws_fields["logGroup"] is not None:
        # add the service and function to the fields
        extra = split_log_group(aws_fields["logGroup"])
        if extra is not None:
            aws_fields.update(extra)

    events = []
    for log_event in data["logEvents"]:
        message = log_event["message"]
        ev = {
            "_time": log_event["timestamp"] * 1000,
            "aws": aws_fields,
            "message": log_event["message"],
        }
        if os.getenv("DISABLE_JSON", "false").lower() not in ("true", "1", "t"):
            msg = parse_message(message)
            if len(msg) == 0:
                msg = message

            json_data = structured_message(msg)
            data = json_data if json_data is not None else msg
            data = {aws_fields["serviceName"]: data}
            if data != None:
                ev.update(data)

        events.append(ev)

    try:
        push_events_to_axiom(events)
    except Exception as e:
        logger.error(f"Error pushing events to axiom: {e}")
        raise e
