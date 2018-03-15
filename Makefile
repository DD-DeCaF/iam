.PHONY: network start setup databases keypair qa test unittest flake8 isort isort-save license pipenv-check stop clean logs

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Create the external iloop network
network:
	docker network inspect iloop >/dev/null || docker network create iloop

## Install and start the service.
start: network
	docker-compose up -d --build

## Create initial databases and RSA keys. You must only run this once.
setup: network databases keypair

## Create initial databases. You must only run this once.
databases:
	docker-compose up -d
	docker-compose exec postgres psql -U postgres -c "create database iam;"
	docker-compose exec postgres psql -U postgres -c "create database iam_test;"
	docker-compose exec web flask db upgrade
	# note: not migrating iam_test db; tests will create and tear down tables
	docker-compose stop

## Create RSA keypair used for signing JWTs.
keypair:
	docker-compose run --rm web ssh-keygen -t rsa -b 2048 -f keys/rsa -N ""

## Run all QA targets
qa: test flake8 isort license pipenv-check

## Run the tests
test:
	docker-compose run --rm -e ENVIRONMENT=testing web py.test --cov=iam tests

## Run only unit tests
unittest:
	docker-compose run --rm -e ENVIRONMENT=testing web py.test --cov=iam tests/unit

## Run flake8
flake8:
	docker-compose run --rm web flake8 iam tests

## Check import sorting
isort:
	docker-compose run --rm web isort --check-only --recursive iam tests

## Sort imports and write changes to files
isort-save:
	docker-compose run --rm web isort --recursive iam tests

## Verify source code license headers
license:
	./scripts/verify_license_headers.sh iam

## Check for known vulnerabilities in python dependencies
pipenv-check:
	pipenv check

## Shut down the Docker containers.
stop:
	docker-compose stop

## Remove all containers.
clean:
	docker-compose down

## Read the logs.
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
