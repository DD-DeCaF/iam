import os
import pathlib
from datetime import timedelta


class Default:
    SERVICE_URL = os.environ['SERVICE_URL']
    FEAT_AUTH = os.environ['FEAT_AUTH']
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SENTRY_DSN = os.environ['SENTRY_DSN']

    BASIC_AUTH_USERNAME = os.environ['BASIC_AUTH_USERNAME']
    BASIC_AUTH_PASSWORD = os.environ['BASIC_AUTH_PASSWORD']

    RSA_PRIVATE_KEY = pathlib.Path('keys/rsa').read_text()
    ALGORITHM = 'RS512'
    JWT_VALIDITY = timedelta(minutes=10)
    REFRESH_TOKEN_VALIDITY = timedelta(days=30)


class Development(Default):
    DEBUG = True
    SECRET_KEY = os.urandom(24)


class Production(Default):
    DEBUG = False
    SECRET_KEY = os.environ['SECRET_KEY']


if os.environ['CONFIGURATION'] == 'prod':
    Settings = Production
else:
    Settings = Development
