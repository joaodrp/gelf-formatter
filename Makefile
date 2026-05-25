.SILENT: ;
.DEFAULT_GOAL := help

lint: ## Run linters
	uv tool run ruff check
	uv tool run ruff format --check

typecheck: ## Run type checker
	uv run --with mypy mypy gelfformatter

test: ## Run test suite with coverage
	uv run --with pytest --with pytest-cov pytest --cov=gelfformatter --cov-report=term-missing

ci: lint typecheck test ## Run all checks (matches CI)

clean: ## Remove build artifacts and caches
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .ruff_cache/ .mypy_cache/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -type d -exec rm -rf {} +

help: ## Display this help
	awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / \
	{printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: lint typecheck test ci clean help
