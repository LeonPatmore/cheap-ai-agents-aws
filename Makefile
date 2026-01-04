up:
	@if [ "$$CI" = "true" ]; then \
		CHANGED_FILES=$$(git diff --name-only HEAD~1 2>/dev/null || git diff --name-only origin/master 2>/dev/null || echo "unknown"); \
		if echo "$$CHANGED_FILES" | grep -qE '\.(md|txt|rst)$$' && ! echo "$$CHANGED_FILES" | grep -qvE '\.(md|txt|rst)$$'; then \
			echo "Skipping deployment in CI - only documentation files changed: $$CHANGED_FILES"; \
		else \
			docker-compose up; \
		fi \
	else \
		docker-compose up; \
	fi

state-delete-service:
	docker-compose run --rm pulumi pulumi state delete 'urn:pulumi:dev::aws-cheap-ai-agents::aws:apprunner/service:Service::dockerhubMcpServer' --yes
