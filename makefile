# Used by `image`, `push` & `deploy` targets, override as required
IMAGE_REG ?= gitlab.rrze.fau.de:4567
IMAGE_REPO ?= evt/klaeffizient/bsm2-python
IMAGE_TAG ?= latest

# Don't change
SRC_DIR := src

.PHONY: help lint lint-fix image push run deploy undeploy clean test-api .EXPORT_ALL_VARIABLES
.DEFAULT_GOAL := help

help:  ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

lint: venv  ## Lint & format, will not fix but sets exit code on error 
	. $(SRC_DIR)/.venv/bin/activate \
	&& black --check $(SRC_DIR) \
	&& flake8 $(SRC_DIR)

lint-fix: venv  ## Lint & format, will try to fix errors and modify code
	. $(SRC_DIR)/.venv/bin/activate \
	&& black $(SRC_DIR)

image:  ## Build container image from Dockerfile 
	docker build . --file Dockerfile \
	--tag $(IMAGE_REG)/$(IMAGE_REPO):$(IMAGE_TAG)

push:  ## Push container image to registry 
	docker push $(IMAGE_REG)/$(IMAGE_REPO):$(IMAGE_TAG)

run: venv  ## Run the main script once
	. $(SRC_DIR)/.venv/bin/activate \
	&& python src/sim_methanation.py

test: venv  ## Unit tests for repo
	. $(SRC_DIR)/.venv/bin/activate \
	&& pytest -v tests/

test-report: venv  ## Unit tests for repo (with report output)
	. $(SRC_DIR)/.venv/bin/activate \
	&& pytest -v --junitxml=test-results.xml

clean:  ## Clean up project
	rm -rf $(SRC_DIR)/.venv
	rm -rf tests/node_modules
	rm -rf tests/package*
	rm -rf test-results.xml
	rm -rf .pytest_cache
	rm -rf $(SRC_DIR)/.pytest_cache

# ============================================================================

venv: $(SRC_DIR)/.venv/touchfile

$(SRC_DIR)/.venv/touchfile: requirements.txt
	python3 -m venv $(SRC_DIR)/.venv
	. $(SRC_DIR)/.venv/bin/activate; pip install -Ur requirements.txt
	touch $(SRC_DIR)/.venv/touchfile
