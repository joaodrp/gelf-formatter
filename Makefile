.SILENT: ;
.DEFAULT_GOAL := help

.PHONY: setup

setup: ## Get development dependencies
	pip install --upgrade pip setuptools pipenv
	pipenv --python 3.7
	pipenv shell
	pipenv install

.PHONY: clean-build
clean-build:
	rm -rf build/
	rm -rf dist/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -rf {} +

.PHONY: clean-pyc
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

.PHONY: clean-test
clean-test:
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/

.PHONY: clean
clean: clean-build clean-pyc clean-test ## Remove object and cache files

.PHONY: dist
dist: clean ## Package
	pipenv run python setup.py sdist bdist_wheel
	ls -l dist

.PHONY: publish
publish: clean ## Publish package
	pipenv run twine upload dist/*

.PHONY: lint
lint: ## Run linters
	pipenv run flake8
	pipenv run black --check .

.PHONY: test
test: ## Run test suite
	pipenv run python -m unittest discover -v

.PHONY: test-all
test-all: ## Run all tests
	pipenv run tox

.PHONY: coverage
coverage: ## Generate test coverage report
	pipenv run coverage run -m --branch unittest discover -v
	pipenv run coverage report -m --include='gelfformatter/*'
	pipenv run coverage html

.PHONY: ci
ci: coverage lint ## Run all tests and code checks

.PHONY: help
help: ## Display this help
	awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / \
	{printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
