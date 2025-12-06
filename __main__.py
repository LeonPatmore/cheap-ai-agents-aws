import json
import pulumi
import pulumi_aws as aws

# Create an IAM role for App Runner
app_runner_role = aws.iam.Role(
    "appRunnerRole",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "build.apprunner.amazonaws.com",
                },
                "Action": "sts:AssumeRole",
            },
        ],
    }),
)


# Create the App Runner service
app_runner_service = aws.apprunner.Service(
    "slackMcpServer",
    service_name="slack-mcp-server",
    source_configuration=aws.apprunner.ServiceSourceConfigurationArgs(
        image_repository=aws.apprunner.ServiceSourceConfigurationImageRepositoryArgs(
            image_identifier="public.ecr.aws/docker/library/mcp/slack:latest",
            image_repository_type="ECR_PUBLIC",
            image_configuration=aws.apprunner.ServiceSourceConfigurationImageRepositoryImageConfigurationArgs(
                port="3000",  # Default port for MCP servers, adjust if needed
                runtime_environment_variables={
                    # Add any required environment variables here
                    # For example: "SLACK_BOT_TOKEN": "...", "SLACK_APP_TOKEN": "..."
                },
            ),
        ),
        auto_deployments_enabled=False,
    ),
    instance_configuration=aws.apprunner.ServiceInstanceConfigurationArgs(
        cpu="0.25 vCPU",
        memory="0.5 GB",
        instance_role_arn=app_runner_role.arn,
    ),
    health_check_configuration=aws.apprunner.ServiceHealthCheckConfigurationArgs(
        protocol="HTTP",
        path="/health",  # Adjust based on the actual health check endpoint
        interval=10,
        timeout=5,
        healthy_threshold=1,
        unhealthy_threshold=5,
    ),
)

# Export the service URL
pulumi.export("service_url", app_runner_service.service_url)
pulumi.export("service_arn", app_runner_service.arn)
pulumi.export("service_name", app_runner_service.service_name)

