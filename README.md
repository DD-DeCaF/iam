# iam

Identity and access management

[![Build Status](https://travis-ci.org/DD-DeCaF/iam.svg?branch=devel)](https://travis-ci.org/DD-DeCaF/iam)
[![Codecov](https://codecov.io/gh/DD-DeCaF/iam/branch/devel/graph/badge.svg)](https://codecov.io/gh/DD-DeCaF/iam)
[![Requirements Status](https://requires.io/github/DD-DeCaF/iam/requirements.svg?branch=devel)](https://requires.io/github/DD-DeCaF/iam/requirements/?branch=devel)

## Development

Type `make` to see all make targets.

Note that DD-DeCaF services are expected to be connected to the `iloop` Docker network.

### Environment

Create a local `.env` file to override environment variables.

* `CONFIGURATION` (default: `DEV`): Set to `DEV` for development configuration, or `PROD` for production configuration
* `SECRET_KEY` (default: random) Flask secret key
