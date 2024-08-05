import json
import http.client
from urllib.parse import urlparse
from typing import Optional

log_groups_return_limit = 50

def send_response(event, context, response_status, response_data):
    response_body = json.dumps(
        {
            "Status": response_status,
            "Reason": "See the details in CloudWatch Log Stream: "
            + context.log_stream_name,
            "PhysicalResourceId": context.log_stream_name or context.aws_request_id,
            "StackId": event["StackId"],
            "RequestId": event["RequestId"],
            "LogicalResourceId": event["LogicalResourceId"],
            "Data": response_data,
        }
    )

    parsed_url = urlparse(event["ResponseURL"])
    if parsed_url.scheme == "https":
        conn = http.client.HTTPSConnection(parsed_url.hostname)
    else:
        conn = http.client.HTTPConnection(parsed_url.hostname)

    conn.request(
        "PUT",
        parsed_url.path + "?" + parsed_url.query,
        body=response_body,
        headers={"Content-Type": ""},
    )

    response = conn.getresponse()
    if response.status < 200 or response.status >= 300:
        raise Exception(
            f"Failed to send response to CloudFormation. HTTP status code: {response.status}"
        )
    conn.close()


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

def fetch_log_groups(cloudwatch_logs_client):
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
