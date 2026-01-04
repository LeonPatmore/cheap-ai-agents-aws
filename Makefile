up:
	@if [ "$$CI" = "true" ] && [ "$$SKIP_DEPLOYMENT" = "true" ]; then \
		echo "Skipping deployment in CI for documentation-only changes"; \
	else \
		docker-compose up; \
	fi

state-delete-service:
	docker-compose run --rm pulumi pulumi state delete 'urn:pulumi:dev::aws-cheap-ai-agents::aws:apprunner/service:Service::dockerhubMcpServer' --yes
