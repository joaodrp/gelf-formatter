.SILENT: ;
.DEFAULT_GOAL := help

setup: ## Get development dependencies
	pip install pipenv --upgrade
	pipenv install --dev

clean-build:
	rm -rf build/
	rm -rf dist/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -rf {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-test:
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/

clean: clean-build clean-pyc clean-test ## Remove object and cache files

lint: ## Run linters
	pipenv run flake8
	pipenv run black --check .
	isort --check-only

test: ## Run test suite
	pipenv run python -m unittest discover -v

test-all: ## Run all tests
	pipenv run tox

coverage: ## Generate test coverage report
	pipenv run coverage run -m --branch unittest discover -v
	pipenv run coverage report -m --include='gelfformatter/*'

coverage-html: coverage ## Generate HTML test coverage report
	pipenv run coverage html

ci: lint coverage ## Run all tests and code checks

.PHONY: dist
dist: clean ## Package
	pipenv run python setup.py sdist bdist_wheel
	ls -l dist

publish: dist ## Publish package
	pipenv run twine upload dist/*

help: ## Display this help
	awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / \
	{printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
