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

## Development

Prerequisites: Docker, make and pipenv. Run `make setup` once to create the database, run migrations and create a local RSA keypair. Type `make` to see all make targets.

### Environment

Specify environment variables in `docker-compose.yml`. See the file for default development values.

* `ENVIRONMENT`: Set to `development`, `testing` or `production`
* `SECRET_KEY`: Flask secret key. Will be randomly generated in dev/testing envs
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

## API

### Admin UI

`GET /admin`

### Authenticate as local user

`POST /authenticate/local`

Parameters:

* `email`
* `password`

Returns:

    {
      'jwt': <Signed JWT>,
      'refresh_token': {
        'val': <Refresh Token>,
        'exp': <Expiry (unix time)>,
      },
    }

### Authenticate as Firebase user

`POST /authenticate/firebase`

Parameters:

* `uid`
* `token`

Returns:

    {
      'jwt': <Signed JWT>,
      'refresh_token': {
        'val': <Refresh Token>,
        'exp': <Expiry (unix time)>,
      },
    }

### Refresh JWT

`POST /refresh`

Parameters:

* `refresh_token`

Returns:

    <Signed JWT>

### Get signing keys

`GET /keys`

Returns:

    <JWK>

See also: [RFC 7517](https://tools.ietf.org/html/rfc7517) or [the OpenID Connect implementation](https://connect2id.com/products/server/docs/api/jwk-set#keys).
