import os
import pathlib
from datetime import timedelta


class Default:
    SERVICE_URL = os.environ['SERVICE_URL']
    RSA_PRIVATE_KEY = pathlib.Path('keys/rsa').read_text()
    ALGORITHM = 'RS512'
    JWT_VALIDITY = timedelta(minutes=10)
    REFRESH_TOKEN_VALIDITY = timedelta(days=30)
    SENTRY_DSN = os.environ['SENTRY_DSN']

    BASIC_AUTH_USERNAME = os.environ['BASIC_AUTH_USERNAME']
    BASIC_AUTH_PASSWORD = os.environ['BASIC_AUTH_PASSWORD']

    FEAT_TOGGLE_LOCAL_AUTH = bool(os.environ['FEAT_TOGGLE_LOCAL_AUTH'])
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FEAT_TOGGLE_FIREBASE = bool(os.environ['FEAT_TOGGLE_FIREBASE'])
    FIREBASE_CLIENT_CERT_URL = os.environ.get('FIREBASE_CLIENT_CERT_URL')
    FIREBASE_CLIENT_EMAIL = os.environ.get('FIREBASE_CLIENT_EMAIL')
    FIREBASE_CLIENT_ID = os.environ.get('FIREBASE_CLIENT_ID')
    FIREBASE_PRIVATE_KEY = os.environ.get('FIREBASE_PRIVATE_KEY')
    FIREBASE_PRIVATE_KEY_ID = os.environ.get('FIREBASE_PRIVATE_KEY_ID')
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')

    FEAT_TOGGLE_OIDC = bool(os.environ['FEAT_TOGGLE_OIDC'])
    OIDC_DISCOVERY_URL = os.environ.get('OIDC_DISCOVERY_URL')
    OIDC_CLIENT_ID = os.environ.get('OIDC_CLIENT_ID')
    OIDC_CLIENT_SECRET = os.environ.get('OIDC_CLIENT_SECRET')
    OIDC_REDIRECT_BASE = os.environ.get('OIDC_REDIRECT_BASE')


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
