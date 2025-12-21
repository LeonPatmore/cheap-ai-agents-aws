# AWS App Runner - Docker Hub MCP Server

Deploy the Docker Hub MCP server container to AWS App Runner using Pulumi.

## Prerequisites

- Docker and Docker Compose
- AWS credentials: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

## Setup

Set AWS credentials:
```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
```

## Deployment

```bash
make up
```

First run builds a custom Docker image. Stack initializes automatically.

**Get service URL:**
```bash
docker-compose run --rm pulumi pulumi stack output service_url
```

## Configuration

- Container: `docker.io/mcp/dockerhub:latest`
- Port: 3000
- Instance: 0.25 vCPU, 0.5 GB memory
- State: Local (`.pulumi/` directory)

Add environment variables in `__main__.py` under `runtime_environment_variables`.

## Cleanup

```bash
docker-compose run --rm pulumi pulumi destroy --yes
```

TEST_MARKER_6843b642
