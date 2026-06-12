.DEFAULT_GOAL := help
SHELL := /bin/bash

# Use docker compose v2; fall back to legacy if needed.
COMPOSE ?= docker compose

.PHONY: help
help: ## List targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

.PHONY: env
env: ## Create .env from .env.example if missing
	@test -f .env || (cp .env.example .env && echo "Created .env from .env.example")

.PHONY: up
up: env ## Build and start the full stack (db, gateway, web)
	$(COMPOSE) up -d --build
	@echo "gateway: http://localhost:$${GATEWAY_PORT:-8000}/health"
	@echo "web:     http://localhost:$${WEB_PORT:-8080}"

.PHONY: down
down: ## Stop the stack
	$(COMPOSE) down

.PHONY: ps
ps: ## Show running services
	$(COMPOSE) ps

.PHONY: logs
logs: ## Tail logs
	$(COMPOSE) logs -f --tail=100

.PHONY: build
build: ## Build all images
	$(COMPOSE) build

.PHONY: lint
lint: ## Lint and format-check Python
	ruff check .
	ruff format --check .

.PHONY: fmt
fmt: ## Auto-format Python
	ruff check --fix .
	ruff format .

.PHONY: typecheck
typecheck: ## Static type-check Python
	mypy services tests

.PHONY: test
test: ## Run tests
	pytest

.PHONY: secret-scan
secret-scan: ## Scan tracked files for committed secrets
	bash scripts/secret-scan.sh

.PHONY: seed
seed: ## Ingest the knowledge base into pgvector (needs DATABASE_URL)
	python -m services.rag.ingest --reset

.PHONY: agent-demo
agent-demo: ## Run a scripted agent query (offline unless ANTHROPIC_API_KEY is set)
	python -m services.agent --aoi central_valley_ca --before 2023-06-15 --after 2023-09-15

.PHONY: kb-demo
kb-demo: ## Ask a sensor-metadata question answered from the knowledge base (RAG)
	python -m services.agent --kb-only

.PHONY: mcp-tools
mcp-tools: ## List tools exposed by the MCP server over stdio
	python -m services.mcp_server.mcp_client

.PHONY: demo
demo: ## End-to-end demo (lands in Phase 5)
	@echo "demo: end-to-end demo lands in Phase 5"

.PHONY: k8s-up
k8s-up: ## Deploy full stack to a local kind cluster (lands in Phase 6)
	@echo "k8s-up: kind + Helm deploy lands in Phase 6"

.PHONY: clean
clean: ## Stop stack and remove volumes
	$(COMPOSE) down -v
