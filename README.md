# iam

Identity and access management

![Branch](https://img.shields.io/badge/branch-master-blue.svg)
[![Build Status](https://travis-ci.org/DD-DeCaF/iam.svg?branch=master)](https://travis-ci.org/DD-DeCaF/iam)
[![Codecov](https://codecov.io/gh/DD-DeCaF/iam/branch/master/graph/badge.svg)](https://codecov.io/gh/DD-DeCaF/iam/branch/master)
[![Requirements Status](https://requires.io/github/DD-DeCaF/iam/requirements.svg?branch=master)](https://requires.io/github/DD-DeCaF/iam/requirements/?branch=master)

![Branch](https://img.shields.io/badge/branch-devel-blue.svg)
[![Build Status](https://travis-ci.org/DD-DeCaF/iam.svg?branch=devel)](https://travis-ci.org/DD-DeCaF/iam)
[![Codecov](https://codecov.io/gh/DD-DeCaF/iam/branch/devel/graph/badge.svg)](https://codecov.io/gh/DD-DeCaF/iam/branch/devel)
[![Requirements Status](https://requires.io/github/DD-DeCaF/iam/requirements.svg?branch=devel)](https://requires.io/github/DD-DeCaF/iam/requirements/?branch=devel)

## Endpoints

* Admin UI: `/admin`
* OpenAPI JSON: `/openapi.json`
* API docs: See https://docs.dd-decaf.eu

## Development

Prerequisites: Docker, make and pipenv. Run `make setup` once to create the database, run migrations and create a local RSA keypair. Type `make` to see all make targets.

### Environment

Specify environment variables in `.env`. See `docker-compose.yml` for default development values.

* `ENVIRONMENT`: Set to `development`, `testing` or `production`
* `SECRET_KEY`: Flask secret key. Will be randomly generated in dev/testing envs
* `SERVICE_URL`: URL prefix to the API service, defaults to empty
* `ALLOWED_ORIGINS`: Comma-seperated list of CORS allowed origins
* `BASIC_AUTH_USERNAME`: Username to authenticate with admin interface
* `BASIC_AUTH_PASSWORD`: Password to authenticate with admin interface
* `FEAT_TOGGLE_LOCAL_AUTH`: Feature toggle: local user database authentication
* `SQLALCHEMY_DATABASE_URI`: [Database configuration](http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls)
* `FEAT_TOGGLE_FIREBASE`: Feature toggle: firebase authentication
* `FIREBASE_CLIENT_CERT_URL`
* `FIREBASE_CLIENT_EMAIL`
* `FIREBASE_CLIENT_ID`
* `FIREBASE_PRIVATE_KEY`
* `FIREBASE_PRIVATE_KEY_ID`
* `FIREBASE_PROJECT_ID`
