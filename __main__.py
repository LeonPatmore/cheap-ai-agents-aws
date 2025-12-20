import json
import os
import pulumi
import pulumi_aws as aws

# Get the current AWS account ID and region
current = aws.get_caller_identity()
region = aws.get_region()

# Get Docker Hub credentials from Pulumi config
# Set these with: pulumi config set dockerHubUsername <username>
#                 pulumi config set dockerHubPassword <password> --secret
config = pulumi.Config()
docker_hub_username = config.get("dockerHubUsername") or os.getenv("DOCKER_HUB_USERNAME", "")
docker_hub_password = config.get_secret("dockerHubPassword") or pulumi.Output.secret(os.getenv("DOCKER_HUB_TOKEN", ""))

# Create a Secrets Manager secret for Docker Hub credentials
# Format required: {"username": "...", "password": "..."}
docker_hub_secret = aws.secretsmanager.Secret(
    "dockerHubSecret",
    name="ecr-pullthroughcache/docker-hub",
    description="Docker Hub credentials for ECR pull-through cache",
)

# Create the secret version with Docker Hub credentials
# If credentials are not set, create with empty values (you can update via AWS Console or CLI)
docker_hub_secret_version = aws.secretsmanager.SecretVersion(
    "dockerHubSecretVersion",
    secret_id=docker_hub_secret.id,
    secret_string=docker_hub_password.apply(
        lambda pwd: json.dumps({
            "username": docker_hub_username,
            "accessToken": pwd,
        })
    ),
)

# Create an ECR pull-through cache rule for Docker Hub
ecr_pull_through_cache_rule = aws.ecr.PullThroughCacheRule(
    "dockerHubPullThroughCache",
    ecr_repository_prefix="docker.io",
    upstream_registry_url="registry-1.docker.io",
    credential_arn=docker_hub_secret.arn,
)

# Create an IAM role for App Runner
app_runner_role = aws.iam.Role(
    "appRunnerRole",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": [
                        "build.apprunner.amazonaws.com",
                        "tasks.apprunner.amazonaws.com",
                    ],
                },
                "Action": "sts:AssumeRole",
            },
        ],
    }),
)

# Create a policy for CloudWatch logs and ECR access (required for App Runner)
app_runner_policy = aws.iam.RolePolicy(
    "appRunnerPolicy",
    role=app_runner_role.id,
    policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                "Resource": "*",
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ecr:GetAuthorizationToken",
                ],
                "Resource": "*",
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "ecr:BatchImportUpstreamImage",
                ],
                "Resource": f"arn:aws:ecr:{region.name}:{current.account_id}:repository/docker.io/mcp/dockerhub",
            },
        ],
    }),
)


app_runner_service = aws.apprunner.Service(
    "dockerhubMcpServer",
    service_name="dockerhub-mcp-server",
    source_configuration=aws.apprunner.ServiceSourceConfigurationArgs(
        authentication_configuration=aws.apprunner.ServiceSourceConfigurationAuthenticationConfigurationArgs(
            access_role_arn=app_runner_role.arn,
        ),
        image_repository=aws.apprunner.ServiceSourceConfigurationImageRepositoryArgs(
            image_identifier=f"{current.account_id}.dkr.ecr.{region.name}.amazonaws.com/docker.io/mcp/dockerhub:latest",
            image_repository_type="ECR",
            image_configuration=aws.apprunner.ServiceSourceConfigurationImageRepositoryImageConfigurationArgs(
                port="3000",
                start_command="--transport=http",
                runtime_environment_variables={
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
