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

axiom_cloudwatch_lambda_ingester_arn = os.getenv("AXIOM_CLOUDWATCH_LAMBDA_INGESTER_ARN")
log_group_prefix = os.getenv("LOG_GROUP_PREFIX", "")
log_groups_return_limit = int(os.getenv("LOG_GROUPS_LIMIT", 10))


def get_log_groups(token=None):
    if token is None:
        if log_group_prefix != "":
            return cloudwatch_logs_client.describe_log_groups(
                logGroupNamePrefix=log_group_prefix, limit=log_groups_return_limit
            )
        else:
            return cloudwatch_logs_client.describe_log_groups(
                limit=log_groups_return_limit
            )
    else:
        if log_group_prefix != "":
            return cloudwatch_logs_client.describe_log_groups(
                logGroupNamePrefix=log_group_prefix,
                nextToken=token,
                limit=log_groups_return_limit,
            )
        else:
            return cloudwatch_logs_client.describe_log_groups(
                nextToken=token,
                limit=log_groups_return_limit,
            )

def delete_subscription_filter(log_group_arn, lambda_arn):
    try:
        log_group_name = log_group_arn.split(":")[-2]

        logger.info(f"Deleting subscription filter for {log_group_name}...")

        lambda_client.remove_permission(
            FunctionName=lambda_arn,
            StatementId="%s-axiom" % log_group_name.replace("/", "-"),
        )

        cloudwatch_logs_client.delete_subscription_filter(
            logGroupName=log_group_name, filterName="%s-axiom" % log_group_name
        )

        logger.info(
            f"{log_group_name} subscription filter has been deleted successfully."
        )

    except Exception as e:
        logger.error(f"Error deleting Subscription filter: {e}")
        raise e


def create_subscription_filter(log_group_arn, lambda_arn):
    try:
        log_group_name = log_group_arn.split(":")[-2]
        logger.info(f"Creating subscription filter for {log_group_name}...")
        lambda_client.add_permission(
            FunctionName=lambda_arn,
            StatementId="%s-axiom" % log_group_name.replace("/", "-"),
            Action="lambda:InvokeFunction",
            Principal=f"logs.amazonaws.com",
            SourceArn=log_group_arn,
        )

        cloudwatch_logs_client.put_subscription_filter(
            logGroupName=log_group_name,
            filterName="%s-axiom" % log_group_name,
            filterPattern="",
            destinationArn=lambda_arn,
            distribution="ByLogStream",
        )
        logger.info(
            f"{log_group_name} subscription filter has been created successfully."
        )
    except Exception as e:
        logger.error(f"Error create Subscription filter: {e}")
        raise e


def lambda_handler(event: dict, context=None):
    if axiom_cloudwatch_lambda_ingester_arn is None:
        raise Exception("AXIOM_CLOUDWATCH_LAMBDA_INGESTER_ARN is not set")

    def log_groups(token=None):
        groups_response = get_log_groups(token)
        groups = groups_response["logGroups"]
        token = groups_response["nextToken"] if "nextToken" in groups_response else None

        if len(groups) == 0:
            return

        for group in groups:
            try:
                delete_subscription_filter(
                    group["arn"], axiom_cloudwatch_lambda_ingester_arn
                )
            except Exception:
                pass

            try:
                create_subscription_filter(
                    group["arn"], axiom_cloudwatch_lambda_ingester_arn
                )
            except cloudwatch_logs_client.exceptions.LimitExceededException as error:
                print(error)

        if token is None:
            return

        try:
            log_groups(token)
        except Exception as e:
            raise e

    responseData = {}
    try:
        log_groups()
    except Exception as e:
        responseData["success"] = "False"
        if event["ResponseURL"]:
            cfnresponse.send(event, context, cfnresponse.FAILED, responseData)
        else:
            raise e

    responseData["success"] = "True"
    if event["ResponseURL"]:
        cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)
    else:
        return 'ok'
