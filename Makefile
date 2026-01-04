up:
	docker-compose up

ci-validate:
	docker-compose run --rm pulumi sh -c "python -m py_compile __main__.py && echo 'Python syntax check passed'"

state-delete-service:
	docker-compose run --rm pulumi pulumi state delete 'urn:pulumi:dev::aws-cheap-ai-agents::aws:apprunner/service:Service::dockerhubMcpServer' --yes
