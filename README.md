# iam

Identity and access management

![master Branch](https://img.shields.io/badge/branch-master-blue.svg)
[![master Build Status](https://travis-ci.org/DD-DeCaF/iam.svg?branch=master)](https://travis-ci.org/DD-DeCaF/iam)
[![master Codecov](https://codecov.io/gh/DD-DeCaF/iam/branch/master/graph/badge.svg)](https://codecov.io/gh/DD-DeCaF/iam/branch/master)
[![master Requirements Status](https://requires.io/github/DD-DeCaF/iam/requirements.svg?branch=master)](https://requires.io/github/DD-DeCaF/iam/requirements/?branch=master)

![devel Branch](https://img.shields.io/badge/branch-devel-blue.svg)
[![devel Build Status](https://travis-ci.org/DD-DeCaF/iam.svg?branch=devel)](https://travis-ci.org/DD-DeCaF/iam)
[![devel Codecov](https://codecov.io/gh/DD-DeCaF/iam/branch/devel/graph/badge.svg)](https://codecov.io/gh/DD-DeCaF/iam/branch/devel)
[![devel Requirements Status](https://requires.io/github/DD-DeCaF/iam/requirements.svg?branch=devel)](https://requires.io/github/DD-DeCaF/iam/requirements/?branch=devel)

## Endpoints

* Admin UI: `/admin`
* OpenAPI JSON: `/openapi.json`
* API docs: See https://docs.dd-decaf.eu

## Development

Type `make` to see frequently used workflow commands.

### Setup

A local keypair for token signing must be generated, and the databases must be created and migrated. This can be done by running `make setup`.

### Testing

To run all tests and QA checks, run `make qa`.

### Environment

Specify environment variables in a `.env` file. See `docker-compose.yml` for the possible variables and their default values.

* `ENVIRONMENT` Set to either `development`, `testing`, `staging` or `production`.
* `SECRET_KEY` Flask secret key. Will be randomly generated in development and testing environments.
* `SENTRY_DSN` DSN for reporting exceptions to
  [Sentry](https://docs.sentry.io/clients/python/integrations/flask/).
* `ALLOWED_ORIGINS` Comma-seperated list of CORS allowed origins.
* `SERVICE_URL` URL prefix to the API service, defaults to empty
* `BASIC_AUTH_USERNAME` Username to authenticate with admin interface
* `BASIC_AUTH_PASSWORD` Password to authenticate with admin interface
* `FEAT_TOGGLE_LOCAL_AUTH` Feature toggle: local user database authentication
* `DB_HOST` [Database configuration](http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls)
* `DB_PORT`
* `DB_NAME`
* `DB_USERNAME`
* `DB_PASSWORD`
* `FEAT_TOGGLE_FIREBASE`: Feature toggle: firebase authentication
* `FIREBASE_CLIENT_CERT_URL`
* `FIREBASE_CLIENT_EMAIL`
* `FIREBASE_CLIENT_ID`
* `FIREBASE_PRIVATE_KEY`
* `FIREBASE_PRIVATE_KEY_ID`
* `FIREBASE_PROJECT_ID`
