import base64
import gzip
import json
import logging
import os
import re

level = os.getenv("log_level", "INFO")
logging.basicConfig(level=level)
logger = logging.getLogger()
logger.setLevel(level)


# Standard out from Lambdas.
std_matcher = re.compile("\d\d\d\d-\d\d-\d\d\S+\s+(?P<request_id>\S+)")

# END RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
end_matcher = re.compile("END RequestId:\s+(?P<request_id>\S+)")

# START RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
# Version: $LATEST
start_matcher = re.compile(
    "START RequestId:\s+(?P<request_id>\S+)\s+" "Version: (?P<version>\S+)"
)


# REPORT RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
# Duration: 0.47 ms
# Billed Duration: 100 ms
# Memory Size: 128 MB
# Max Memory Used: 20 MB
report_matcher = re.compile(
    "REPORT RequestId:\s+(?P<request_id>\S+)\s+"
    "Duration: (?P<duration>\S+) ms\s+"
    "Billed Duration: (?P<billed_duration>\S+) ms\s+"
    "Memory Size: (?P<memory_size>\S+) MB\s+"
    "Max Memory Used: (?P<max_memory>\S+) MB"
)


# try to get json from message
def structured_message(message: str):
    try:
        return json.loads(message)
    except:
        return None


def push_events_to_axiom(events: list):
    if len(events) == 0:
        return

    # push events to axiom
    axiom_url = os.getenv("AXIOM_URL")
    if axiom_url == None:
        axiom_url = "https://cloud.axiom.co"
    axiom_token = os.getenv("AXIOM_TOKEN")
    axiom_dataset = os.getenv("AXIOM_DATASET")

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
        print(f"Ingested {len(events)} events")


def data_from_event(event: dict) -> dict:
    body = base64.b64decode(event["awslogs"]["data"])
    data = gzip.decompress(body)
    return json.loads(data)


def parse_message(message):
    m = None

    # Determine which matcher to use depending on the message type.
    if message.startswith("END"):
        m = end_matcher.match(message)
    elif message.startswith("START"):
        m = start_matcher.match(message)
    elif message.startswith("REPORT"):
        m = report_matcher.match(message)
    else:
        m = std_matcher.match(message)

    if m:
        return m.groupdict()
    else:
        return {}


def lambda_handler(event: dict, context):
    data = data_from_event(event)

    pattern_obj = re.compile("^/aws/(lambda|apigateway)/(.*)")
    parsed = pattern_obj.match(data.get("", ""))

    aws_fields = {
        "owner": data.get("owner"),
        "log_group": data.get("logGroup"),
        "log_stream": data.get("logStream"),
        "message_type": data.get("messageType"),
        "subscription_filters": data.get("subscriptionFilters"),
        "service_name": parsed.group(1) if parsed else None,
        "parsed_log_group_name": parsed.group(2) if parsed else None,
    }

    events = []
    for log_event in data["logEvents"]:
        message = log_event["message"]
        data = structured_message(message)

        # Create the attributes.
        attributes = {}
        attributes.update(aws_fields)
        attributes.update(parse_message(message))

        # Append the flattened event
        events.append(
            {
                "_time": log_event["timestamp"],
                "raw": message,
                "aws": aws_fields,
                "data": data,
            }
        )

    # push_events_to_axiom(events)
    print(json.dumps(events, indent=2))
