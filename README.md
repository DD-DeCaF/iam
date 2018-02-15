# iam

Identity and access management

[![Build Status](https://travis-ci.org/DD-DeCaF/iam.svg?branch=devel)](https://travis-ci.org/DD-DeCaF/iam)
[![Codecov](https://codecov.io/gh/DD-DeCaF/iam/branch/devel/graph/badge.svg)](https://codecov.io/gh/DD-DeCaF/iam)
[![Requirements Status](https://requires.io/github/DD-DeCaF/iam/requirements.svg?branch=devel)](https://requires.io/github/DD-DeCaF/iam/requirements/?branch=devel)

## Development

Run `make setup` once to create the database, run migrations and create a local RSA keypair. Type `make` to see all make targets.

Note that DD-DeCaF services are expected to be connected to the `iloop` Docker network.

### Environment

Specify environment variables in `docker-compose.yml`. See the file for default development values.

* `CONFIGURATION`: Set to `dev` for development configuration, or `prod` for production configuration
* `SECRET_KEY`: Flask secret key
* `SQLALCHEMY_DATABASE_URI`: [Database configuration](http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls)
* `FEAT_TOGGLE_LOCAL_AUTH`: Feature toggle: local user database authentication
* `FEAT_TOGGLE_FIREBASE`: Feature toggle: firebase authentication
* `BASIC_AUTH_USERNAME`: Username to authenticate with admin interface
* `BASIC_AUTH_PASSWORD`: Password to authenticate with admin interface
