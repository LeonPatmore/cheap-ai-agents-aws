up:
	docker-compose up

state-delete-service:
	docker-compose run --rm pulumi pulumi state delete 'urn:pulumi:dev::aws-cheap-ai-agents::aws:apprunner/service:Service::dockerhubMcpServer' --yes
