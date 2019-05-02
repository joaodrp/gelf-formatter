.SILENT: ;
.DEFAULT_GOAL := help

.PHONY: venv
venv: ## Create and/or activate virtual environment
	test -f .venv/bin/activate || python -m venv .venv
	. .venv/bin/activate;

.PHONY: setup
setup: venv ## Get development dependencies
	pip install --upgrade pip setuptools
	pip install -r requirements.txt -r requirements-dev.txt

.PHONY: clean-build
clean-build:
	rm -rf build/
	rm -rf dist/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +

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
dist: venv clean ## Package
	python setup.py sdist bdist_wheel
	ls -l dist

.PHONY: publish
publish: venv clean ## Publish package
	twine upload dist/*

.PHONY: lint
lint: venv ## Run linters
	flake8
	black --check .

.PHONY: test
test: venv ## Run test suite
	python -m unittest discover -v

.PHONY: test-all
test-all: venv ## Run all tests
	tox

.PHONY: coverage
coverage: venv ## Generate test coverage report
	coverage run -m --branch unittest discover -v
	coverage report -m --include='gelfformatter/*'
	coverage html

.PHONY: ci
ci: coverage lint ## Run all tests and code checks

.PHONY: help
help: ## Display this help
	awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / \
	{printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)