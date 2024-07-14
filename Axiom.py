from aws_cdk import (
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_s3 as s3,
    aws_events as events,
    aws_events_targets as targets,
    aws_cloudtrail as cloudtrail,
)
import aws_cdk as core
from constructs import Construct

class CloudWatchIngester(Construct):

    def __init__(self, scope: Construct, id: str, axiom_token: str, axiom_url: str, axiom_dataset: str, cloudwatch_log_group_names: list, lambda_function_name: str, data_tags: str, disable_json: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        logs_role = iam.Role(self, "LogsRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        lambda_function = lambda_.Function(self, "LogsLambda",
            function_name=lambda_function_name,
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("../",exclude=["cdk","*.yaml","cdk.out",".venv"]),
            role=logs_role,
            environment={
                "AXIOM_TOKEN": axiom_token,
                "AXIOM_DATASET": axiom_dataset,
                "AXIOM_URL": axiom_url,
                "DISABLE_JSON": disable_json,
                "DATA_TAGS": data_tags
            }
        )

        for log_group_name in cloudwatch_log_group_names:
            logs.CfnSubscriptionFilter(self, f"LGSF{log_group_name}",
                log_group_name=log_group_name,
                filter_pattern="",
                destination_arn=lambda_function.function_arn
            )

        lambda_.CfnPermission(self, "LogsLambdaWildcardPermission",
            action="lambda:InvokeFunction",
            function_name=lambda_function.function_name,
            principal=f"logs.{core.Aws.REGION}.amazonaws.com",
            source_account=core.Aws.ACCOUNT_ID,
            source_arn=f"arn:aws:logs:{core.Aws.REGION}:{core.Aws.ACCOUNT_ID}:log-group:*"
        )

        core.CfnOutput(self, "LogsLambdaARN",
            description="The ARN of the created Ingester Lambda",
            value=lambda_function.function_arn,
            export_name=f"{id}-LogsLambdaARN"
        )

class CloudWatchBackfiller(Construct):

    def __init__(self, scope: Construct, id: str, lambda_function_name: str, axiom_cloudwatch_lambda_ingester_arn: str, cloudwatch_log_groups_prefix: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        backfiller_role = iam.Role(self, "BackfillerRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        backfiller_policy = iam.Policy(self, "BackfillerPolicy",
            policy_name="axiom-cloudwatch-backfiller-lambda-policy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "logs:DeleteSubscriptionFilter",
                        "logs:PutSubscriptionFilter",
                        "logs:DescribeLogGroups",
                        "lambda:AddPermission",
                        "lambda:RemovePermission"
                    ],
                    resources=["*"],
                    effect=iam.Effect.ALLOW
                )
            ]
        )
        backfiller_policy.attach_to_role(backfiller_role)

        backfiller_lambda = lambda_.Function(self, "BackfillerLambda",
            function_name=lambda_function_name,
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="backfill.lambda_handler",
            code=lambda_.Code.from_asset("../",exclude=["cdk","*.yaml","cdk.out",".venv"]),
            role=backfiller_role,
            timeout=core.Duration.minutes(5),
            environment={
                "AXIOM_CLOUDWATCH_LAMBDA_INGESTER_ARN": axiom_cloudwatch_lambda_ingester_arn,
                "LOG_GROUP_PREFIX": cloudwatch_log_groups_prefix
            }
        )

        core.CfnOutput(self, "BackfillerLambdaARN",
            description="The ARN of the created Backfiller Lambda",
            value=backfiller_lambda.function_arn,
            export_name=f"{id}-BackfillerLambdaARN"
        )

class CloudWatchSubscriber(Construct):

    def __init__(self, scope: Construct, id: str, lambda_function_name: str, axiom_cloudwatch_lambda_ingester_arn: str, cloudwatch_log_groups_prefix: str, axiom_lambda_log_retention: int, enable_cloudtrail: bool, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        should_enable_cloudtrail = enable_cloudtrail

        if should_enable_cloudtrail:
            s3_bucket = s3.Bucket(self, "AxiomCloudWatchLogsSubscriberS3Bucket",
                bucket_name=f"{core.Aws.STACK_NAME}-cloudtrail",
                access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL
            )

            s3_bucket.add_to_resource_policy(iam.PolicyStatement(
                actions=["s3:GetBucketAcl"],
                principals=[iam.ServicePrincipal("cloudtrail.amazonaws.com")],
                resources=[s3_bucket.bucket_arn],
                effect=iam.Effect.ALLOW
            ))

            s3_bucket.add_to_resource_policy(iam.PolicyStatement(
                actions=["s3:PutObject"],
                principals=[iam.ServicePrincipal("cloudtrail.amazonaws.com")],
                resources=[f"{s3_bucket.bucket_arn}/AWSLogs/{core.Aws.ACCOUNT_ID}/*"],
                effect=iam.Effect.ALLOW,
                conditions={"StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}}
            ))

            cloudtrail.Trail(self, "AxiomLogsSubscriberCloudTrail",
                bucket=s3_bucket,
                trail_name=f"{core.Aws.STACK_NAME}-{core.Aws.ACCOUNT_ID}",
                is_multi_region_trail=True,
                include_global_service_events=True,
                enable_file_validation=False
            )

        subscriber_role = iam.Role(self, "AxiomCloudWatchLogsSubscriberRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        subscriber_policy = iam.Policy(self, "AxiomCloudWatchLogsSubscriberPolicy",
            policy_name="cloudwatch-subscriber-axiom-policy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "logs:DeleteSubscriptionFilter",
                        "logs:PutSubscriptionFilter",
                        "logs:DescribeLogGroups",
                        "lambda:AddPermission",
                        "lambda:RemovePermission",
                        "lambda:InvokeFunction",
                        "lambda:GetFunction",
                        "logs:DescribeLogStreams",
                        "logs:DescribeSubscriptionFilters",
                        "logs:FilterLogEvents",
                        "logs:GetLogEvents"
                    ],
                    resources=["*"],
                    effect=iam.Effect.ALLOW
                )
            ]
        )
        subscriber_policy.attach_to_role(subscriber_role)
        

        subscriber_lambda = lambda_.Function(self, "AxiomCloudWatchLogsSubscriber",
            function_name=lambda_function_name,
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="logs_subscriber.lambda_handler",
            code=lambda_.Code.from_asset("../",exclude=["cdk","*.yaml","cdk.out",".venv"]),
            role=subscriber_role,
            environment={
                "AXIOM_CLOUDWATCH_LAMBDA_INGESTER_ARN": axiom_cloudwatch_lambda_ingester_arn,
                "LOG_GROUP_PREFIX": cloudwatch_log_groups_prefix
            },
            log_retention=logs.RetentionDays.ONE_DAY if axiom_lambda_log_retention == 1 else axiom_lambda_log_retention
        )

        event_rule = events.Rule(self, "AxiomLogsSubscriberEventRule",
            description="Axiom log group auto subscription event rule.",
            event_pattern={
                "source": ["aws.logs"],
                "detail": {
                    "eventSource": ["logs.amazonaws.com"],
                    "eventName": ["CreateLogGroup"]
                }
            }
        )
        event_rule.add_target(targets.LambdaFunction(subscriber_lambda))

        lambda_.CfnPermission(self, "AxiomCloudWatchLogsSubscriberPermission",
            action="lambda:InvokeFunction",
            function_name=subscriber_lambda.function_arn,
            principal="events.amazonaws.com",
            source_account=core.Aws.ACCOUNT_ID,
            source_arn=event_rule.rule_arn
        )

        logs.LogGroup(self, "AxiomCloudWatchLogsSubscriberLogGroup",
            log_group_name=f"/aws/lambda/{lambda_function_name}",
            retention=logs.RetentionDays.ONE_DAY if axiom_lambda_log_retention == 1 else axiom_lambda_log_retention
        )

        core.CfnOutput(self, "SubscriberLambdaARN",
            description="The ARN of the created Subscriber Lambda",
            value=subscriber_lambda.function_arn,
            export_name=f"{id}-SubscriberLambdaARN"
        )

class AxiomStack(core.Stack):

    def __init__(self, scope: Construct, id: str, axiom_token: str, axiom_url: str, axiom_dataset: str, cloudwatch_log_group_names: list, ingester_lambda_function_name: str, backfiller_lambda_function_name: str, subscriber_lambda_function_name: str, data_tags: str, disable_json: str, cloudwatch_log_groups_prefix: str, axiom_lambda_log_retention: int, enable_cloudtrail: bool, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        ingester = CloudWatchIngester(self, "CloudWatchIngester",
            axiom_token=axiom_token,
            axiom_url=axiom_url,
            axiom_dataset=axiom_dataset,
            cloudwatch_log_group_names=cloudwatch_log_group_names,
            lambda_function_name=ingester_lambda_function_name,
            data_tags=data_tags,
            disable_json=disable_json
        )

        backfiller = CloudWatchBackfiller(self, "CloudWatchBackfiller",
            lambda_function_name=backfiller_lambda_function_name,
            axiom_cloudwatch_lambda_ingester_arn=core.Fn.import_value("CloudWatchIngester-LogsLambdaARN"),
            cloudwatch_log_groups_prefix=cloudwatch_log_groups_prefix
        )

        subscriber = CloudWatchSubscriber(self, "CloudWatchSubscriber",
            lambda_function_name=subscriber_lambda_function_name,
            axiom_cloudwatch_lambda_ingester_arn=core.Fn.import_value("CloudWatchIngester-LogsLambdaARN"),
            cloudwatch_log_groups_prefix=cloudwatch_log_groups_prefix,
            axiom_lambda_log_retention=axiom_lambda_log_retention,
            enable_cloudtrail=enable_cloudtrail
        )