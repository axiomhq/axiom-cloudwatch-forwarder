from datetime import datetime
from aws_cdk import (
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_s3 as s3,
    aws_events as events,
    aws_events_targets as targets,
    aws_cloudtrail as cloudtrail,
    custom_resources as cr,
)
import aws_cdk as core
from constructs import Construct


class CloudWatchForwarder(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        axiom_token: str,
        axiom_url: str,
        axiom_dataset: str,
        data_tags: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        log_group = logs.LogGroup(
            self,
            "ForwarderLogGroup",
            log_group_name="/aws/axiom/forwarder",
            retention=logs.RetentionDays.ONE_DAY,
        )
        log_group.apply_removal_policy(core.RemovalPolicy.DESTROY)

        lambda_function = lambda_.Function(
            self,
            "Lambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="forwarder.lambda_handler",
            code=lambda_.Code.from_asset(
                "./src",
                exclude=[
                    "cdk",
                    "*.yaml",
                    "cdk.out",
                    ".venv",
                    "Pipfile*",
                    "requirements.txt",
                ],
            ),
            environment={
                "AXIOM_TOKEN": axiom_token,
                "AXIOM_DATASET": axiom_dataset,
                "AXIOM_URL": axiom_url,
                "DATA_TAGS": data_tags,
            },
            log_group=log_group,
        )

        lambda_.CfnPermission(
            self,
            "WildcardPermission",
            action="lambda:InvokeFunction",
            function_name=lambda_function.function_name,
            principal=f"logs.{core.Aws.REGION}.amazonaws.com",
            source_account=core.Aws.ACCOUNT_ID,
            source_arn=f"arn:aws:logs:{core.Aws.REGION}:{core.Aws.ACCOUNT_ID}:log-group:*:*",
        )

        core.CfnOutput(
            self,
            "ForwarderLambdaARN",
            description="The ARN of the created Forwarder Lambda",
            value=lambda_function.function_arn,
            export_name=f"{id}-ForwarderLambdaARN",
        )
        self.arn = lambda_function.function_arn


class CloudWatchSubscriber(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        axiom_cloudwatch_forwarder_lambda_arn: str,
        cloudwatch_log_groups_names: list,
        cloudwatch_log_groups_prefix: str,
        cloudwatch_log_groups_pattern: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        log_group = logs.LogGroup(
            self,
            "SubscriberLogGroup",
            log_group_name="/aws/axiom/subscriber",
            retention=logs.RetentionDays.ONE_DAY,
        )
        log_group.apply_removal_policy(policy=core.RemovalPolicy.DESTROY)

        subscriber_role = iam.Role(
            self,
            "Role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        subscriber_policy = iam.Policy(
            self,
            "Policy",
            policy_name="axiom-cloudwatch-subscriber-lambda-policy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "logs:DeleteSubscriptionFilter",
                        "logs:PutSubscriptionFilter",
                        "logs:DescribeLogGroups",
                        "lambda:AddPermission",
                        "lambda:RemovePermission",
                    ],
                    resources=["*"],
                    effect=iam.Effect.ALLOW,
                )
            ],
        )
        subscriber_policy.attach_to_role(subscriber_role)

        subscriber_lambda = lambda_.Function(
            self,
            "Lambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="subscriber.lambda_handler",
            code=lambda_.Code.from_asset(
                "./src",
                exclude=[
                    "cdk",
                    "*.yaml",
                    "cdk.out",
                    ".venv",
                    "Pipfile*",
                    "requirements.txt",
                ],
            ),
            role=subscriber_role,
            timeout=core.Duration.minutes(5),
            environment={
                "AXIOM_CLOUDWATCH_FORWARDER_LAMBDA_ARN": axiom_cloudwatch_forwarder_lambda_arn,
                "LOG_GROUP_NAMES": ",".join(cloudwatch_log_groups_names),
                "LOG_GROUP_PREFIX": cloudwatch_log_groups_prefix,
                "LOG_GROUP_PATTERN": cloudwatch_log_groups_pattern,
            },
            log_group=log_group,
        )

        # provider = cr.Provider(
        #     self,
        #     "Provider",
        #     log_retention=logs.RetentionDays.ONE_DAY,
        #     on_event_handler=cr.AwsSdkCall(
        #         service=subscriber_lambda.function_arn,
        #         action="InvokeFunction",
        #         parameters={},
        #     ),
        # )

        # invoker = cr.AwsCustomResource(
        #     self,
        #     "Invoker",
        #     on_create=cr.AwsSdkCall(
        #         service="lambda",
        #         action="InvokeFunction",
        #         physical_resource_id=cr.PhysicalResourceId.of(datetime.now().isoformat()),

        #     ),
        #     policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
        #             resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
        #         )

        # )

        core.CfnOutput(
            self,
            "SubscriberLambdaARN",
            description="The ARN of the created Subscriber Lambda",
            value=subscriber_lambda.function_arn,
            export_name=f"{id}-SubscriberLambdaARN",
        )


class CloudWatchListener(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        axiom_cloudwatch_forwarder_lambda_arn: str,
        cloudwatch_log_groups_prefix: str,
        enable_cloudtrail: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        should_enable_cloudtrail = enable_cloudtrail

        if should_enable_cloudtrail:
            s3_bucket = s3.Bucket(
                self,
                "S3Bucket",
                bucket_name=f"{core.Aws.STACK_NAME}-cloudtrail",
                access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
            )

            s3_bucket.add_to_resource_policy(
                iam.PolicyStatement(
                    actions=["s3:GetBucketAcl"],
                    principals=[iam.ServicePrincipal("cloudtrail.amazonaws.com")],
                    resources=[s3_bucket.bucket_arn],
                    effect=iam.Effect.ALLOW,
                )
            )

            s3_bucket.add_to_resource_policy(
                iam.PolicyStatement(
                    actions=["s3:PutObject"],
                    principals=[iam.ServicePrincipal("cloudtrail.amazonaws.com")],
                    resources=[
                        f"{s3_bucket.bucket_arn}/AWSLogs/{core.Aws.ACCOUNT_ID}/*"
                    ],
                    effect=iam.Effect.ALLOW,
                    conditions={
                        "StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}
                    },
                )
            )

            cloudtrail.Trail(
                self,
                "CloudTrail",
                bucket=s3_bucket,
                trail_name=f"{core.Aws.STACK_NAME}-{core.Aws.ACCOUNT_ID}",
                is_multi_region_trail=True,
                include_global_service_events=True,
                enable_file_validation=False,
            )

        listener_role = iam.Role(
            self,
            "Role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        listener_policy = iam.Policy(
            self,
            "Policy",
            policy_name="cloudwatch-listener-axiom-policy",
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
                        "logs:GetLogEvents",
                    ],
                    resources=["*"],
                    effect=iam.Effect.ALLOW,
                )
            ],
        )
        listener_policy.attach_to_role(listener_role)

        log_group = logs.LogGroup(
            self,
            "ListenerLogGroup",
            log_group_name="/aws/axiom/listener",
            retention=logs.RetentionDays.ONE_DAY,
        )

        listener_lambda = lambda_.Function(
            self,
            "Lambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="listener.lambda_handler",
            code=lambda_.Code.from_asset(
                "./src",
                exclude=[
                    "cdk",
                    "*.yaml",
                    "cdk.out",
                    ".venv",
                    "Pipfile*",
                    "requirements.txt",
                ],
            ),
            role=listener_role,
            environment={
                "AXIOM_CLOUDWATCH_FORWARDER_LAMBDA_ARN": axiom_cloudwatch_forwarder_lambda_arn,
                "LOG_GROUP_PREFIX": cloudwatch_log_groups_prefix,
            },
            log_group=log_group,
        )

        event_rule = events.Rule(
            self,
            "EventRule",
            description="Axiom log group auto subscription event rule.",
            event_pattern={
                "source": ["aws.logs"],
                "detail": {
                    "eventSource": ["logs.amazonaws.com"],
                    "eventName": ["CreateLogGroup"],
                },
            },
        )
        event_rule.add_target(targets.LambdaFunction(listener_lambda))

        lambda_.CfnPermission(
            self,
            "ermission",
            action="lambda:InvokeFunction",
            function_name=listener_lambda.function_arn,
            principal="events.amazonaws.com",
            source_account=core.Aws.ACCOUNT_ID,
            source_arn=event_rule.rule_arn,
        )

        core.CfnOutput(
            self,
            "ListenerLambdaARN",
            description="The ARN of the created Listener Lambda",
            value=listener_lambda.function_arn,
            export_name=f"{id}-ListenerLambdaARN",
        )


class AxiomCloudWatchStack(core.Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        axiom_token: str,
        axiom_url: str,
        axiom_dataset: str,
        data_tags: str,
        cloudwatch_log_groups_names: list,
        cloudwatch_log_groups_prefix: str,
        cloudwatch_log_groups_pattern: str,
        install_listner: bool = False,
        enable_cloudtrail: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        forwarder = CloudWatchForwarder(
            self,
            "Forwarder",
            axiom_token=axiom_token,
            axiom_url=axiom_url,
            axiom_dataset=axiom_dataset,
            data_tags=data_tags,
        )

        subscriber = CloudWatchSubscriber(
            self,
            "Subscriber",
            axiom_cloudwatch_forwarder_lambda_arn=forwarder.arn,
            cloudwatch_log_groups_names=cloudwatch_log_groups_names,
            cloudwatch_log_groups_prefix=cloudwatch_log_groups_prefix,
            cloudwatch_log_groups_pattern=cloudwatch_log_groups_pattern,
        )

        if install_listner:
            listener = CloudWatchListener(
                self,
                "Listener",
                axiom_cloudwatch_forwarder_lambda_arn=forwarder.arn,
                cloudwatch_log_groups_prefix=cloudwatch_log_groups_prefix,
                enable_cloudtrail=enable_cloudtrail,
            )
