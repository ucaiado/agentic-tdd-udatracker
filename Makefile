SHELL := /bin/bash
DEFAULT_GOAL := help
LINT_FILE ?= src/backend/order_tracker.py

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# Docker Management
docker-build:  ## Build the Docker image
	docker-compose build

bash:  ## Open an interactive terminal in Docker container
	docker-compose run --rm udatracker bash

# Application
run-app:  ## Run the Flask application (access at http://localhost:5000)
	docker-compose run --rm --service-ports udatracker python -m backend.app

# Code Quality
lint-files:  ## Run ruff and pylint on specified file (PARAMETER: LINT_FILE)
	docker-compose run --rm udatracker bash -c "ruff format $(LINT_FILE) && ruff check $(LINT_FILE) --fix && pylint $(LINT_FILE)"

# Tests
test-unit:  ## Run OrderTracker unit tests
	docker-compose run --rm udatracker bash -c "cd /app/src && pytest backend/tests/test_order_tracker.py -vv"

test-api:  ## Run API integration tests
	docker-compose run --rm udatracker bash -c "cd /app/src && pytest backend/tests/test_api.py -vv"

test-all:  ## Run the full test suite
	docker-compose run --rm udatracker bash -c "cd /app/src && pytest -vv"
