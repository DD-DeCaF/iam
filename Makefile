.PHONY: setup network keypair databases lock build start qa style test \
		test-travis flake8 isort isort-save license stop clean logs
SHELL:=/bin/bash


#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Run all initialization targets. You must only run this once.
setup: network keypair databases

## Create the docker bridge network if necessary.
network:
	docker network inspect DD-DeCaF >/dev/null 2>&1 || \
		docker network create DD-DeCaF

## Generate Pipfile.lock.
lock:
	docker-compose run --rm web pipenv lock

## Build local docker images.
build:
	docker-compose build

## Start all services in the background.
start:
	docker-compose up -d

## Create RSA keypair used for signing JWTs.
keypair:
	docker-compose run --rm web ssh-keygen -t rsa -b 2048 -f keys/rsa -N ""

## Create initial databases. You must only run this once.
databases:
	docker-compose up -d postgres
	./scripts/wait_for_postgres.sh
	docker-compose exec postgres psql -U postgres -c "create database iam;"
	docker-compose exec postgres psql -U postgres -c "create database iam_test;"
	docker-compose run --rm web flask db upgrade
	docker-compose stop
	# note: not migrating iam_test db; tests will create and tear down tables

## Run all QA targets.
qa: style pipenv-check test

## Run all style related targets.
style: flake8 isort license

## Run flake8.
flake8:
	docker-compose run --rm web flake8 src/iam tests

## Check Python package import order.
isort:
	docker-compose run --rm web isort --check-only --recursive src/iam tests

## Sort imports and write changes to files.
isort-save:
	docker-compose run --rm web isort --recursive src/iam tests

## Verify source code license headers.
license:
	./scripts/verify_license_headers.sh src/iam tests

## Check for known vulnerabilities in python dependencies.
pipenv-check:
	docker-compose run --rm web pipenv check --system

## Run the tests.
test:
	docker-compose run --rm -e ENVIRONMENT=testing -e DB_NAME=iam_test web pytest -s --cov=src/iam tests

## Run the tests and report coverage (see https://docs.codecov.io/docs/testing-with-docker).
shared := /tmp/coverage
test-travis:
	mkdir "$(shared)"
	docker-compose run --rm -e ENVIRONMENT=testing -e DB_NAME=iam_test -v "$(shared):$(shared)" web pytest -s --cov-config=.travis-covrc --cov
	bash <(curl -s https://codecov.io/bash) -f "$(shared)/.coverage"

## Stop all services.
stop:
	docker-compose stop

## Stop all services and remove containers.
clean:
	docker-compose down

## Follow the logs.
logs:
	docker-compose logs --tail="all" -f

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := show-help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: show-help
show-help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
