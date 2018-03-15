# Copyright 2018 Novo Nordisk Foundation Center for Biosustainability, DTU.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pathlib
from datetime import timedelta


class Default:
    SERVICE_URL = os.environ['SERVICE_URL']
    CORS_ORIGINS = os.environ['ALLOWED_ORIGINS'].split(',')
    RSA_PRIVATE_KEY = pathlib.Path('keys/rsa').read_text()
    ALGORITHM = 'RS512'
    JWT_VALIDITY = timedelta(minutes=10)
    REFRESH_TOKEN_VALIDITY = timedelta(days=30)
    SENTRY_DSN = os.environ.get('SENTRY_DSN')

    BASIC_AUTH_USERNAME = os.environ['BASIC_AUTH_USERNAME']
    BASIC_AUTH_PASSWORD = os.environ['BASIC_AUTH_PASSWORD']

    FEAT_TOGGLE_LOCAL_AUTH = bool(os.environ['FEAT_TOGGLE_LOCAL_AUTH'])
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FEAT_TOGGLE_FIREBASE = bool(os.environ['FEAT_TOGGLE_FIREBASE'])
    FIREBASE_CLIENT_CERT_URL = os.environ.get('FIREBASE_CLIENT_CERT_URL')
    FIREBASE_CLIENT_EMAIL = os.environ.get('FIREBASE_CLIENT_EMAIL')
    FIREBASE_CLIENT_ID = os.environ.get('FIREBASE_CLIENT_ID')
    FIREBASE_PRIVATE_KEY = os.environ.get('FIREBASE_PRIVATE_KEY')
    FIREBASE_PRIVATE_KEY_ID = os.environ.get('FIREBASE_PRIVATE_KEY_ID')
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')


class Development(Default):
    DEBUG = True
    SECRET_KEY = os.urandom(24)


class Testing(Default):
    DEBUG = True
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = "postgres://postgres:@postgres:5432/iam_test"


class Production(Default):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')


if os.environ['ENVIRONMENT'] == 'production':
    Settings = Production
elif os.environ['ENVIRONMENT'] == 'testing':
    Settings = Testing
else:
    Settings = Development
