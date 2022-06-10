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
    "Duration: (?P<duration_ns>\S+) ms\s+"
    "Billed Duration: (?P<billed_duration_ms>\S+) ms\s+"
    "Memory Size: (?P<memory_size_mb>\S+) MB\s+"
    "Max Memory Used: (?P<max_memory_mb>\S+) MB"
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
    if message.startswith("REPORT"):
        m = report_matcher.match(message)
        m = m.groupdict()
        # convert from string to number
        m["duration_ns"] = int(float(m["duration_ns"]) * 1000)
        m["billed_duration_ms"] = int(m["billed_duration_ms"])
        m["memory_size_mb"] = int(m["memory_size_mb"])
        m["max_memory_mb"] = int(m["max_memory_mb"])
        return m
    elif message.startswith("END"):
        m = end_matcher.match(message)
    elif message.startswith("START"):
        m = start_matcher.match(message)
    else:
        m = std_matcher.match(message)

    return m.groupdict()


def lambda_handler(event: dict, context=None):
    data = data_from_event(event)

    aws_fields = {
        "owner": data.get("owner"),
        "log_group": data.get("logGroup"),
        "log_stream": data.get("logStream"),
        "message_type": data.get("messageType"),
        "subscription_filters": data.get("subscriptionFilters"),
    }

    # this is an extra field, we can extend this without a problem
    pattern_obj = re.compile("^/aws/(lambda|apigateway|eks|rds)/(.*)")
    parsed = pattern_obj.match(data.get("", ""))
    if parsed:
        aws_fields["service"] = parsed.group(1)
        aws_fields["function"] = parsed.group(2)

    events = []
    for log_event in data["logEvents"]:
        message = log_event["message"]
        ev = {
            "_time": log_event["timestamp"] * 1000,
            "aws": aws_fields,
            "message": log_event["message"],
        }
        if not os.getenv("DISABLE_JSON", "").lower() in ("true", "1", "t"):
            data = structured_message(parse_message(message))
            if data != None:
                ev["fields"] = data

        events.append(ev)

    try:
        push_events_to_axiom(events)
    except Exception as e:
        print(f"Error pushing events to axiom: {e}")
        raise e
