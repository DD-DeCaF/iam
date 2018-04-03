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
    def __init__(self):
        self.SERVICE_URL = os.environ['SERVICE_URL']
        self.CORS_ORIGINS = os.environ['ALLOWED_ORIGINS'].split(',')
        self.RESTPLUS_MASK_SWAGGER = False
        self.RSA_PRIVATE_KEY = pathlib.Path('keys/rsa').read_text()
        self.ALGORITHM = 'RS512'
        self.JWT_VALIDITY = timedelta(minutes=10)
        self.REFRESH_TOKEN_VALIDITY = timedelta(days=30)
        self.SENTRY_DSN = os.environ.get('SENTRY_DSN')

        self.BASIC_AUTH_USERNAME = os.environ['BASIC_AUTH_USERNAME']
        self.BASIC_AUTH_PASSWORD = os.environ['BASIC_AUTH_PASSWORD']

        self.FEAT_TOGGLE_LOCAL_AUTH = bool(os.environ['FEAT_TOGGLE_LOCAL_AUTH'])
        self.SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

        self.FEAT_TOGGLE_FIREBASE = bool(os.environ['FEAT_TOGGLE_FIREBASE'])
        self.FIREBASE_CLIENT_CERT_URL = os.environ.get(
            'FIREBASE_CLIENT_CERT_URL')
        self.FIREBASE_CLIENT_EMAIL = os.environ.get('FIREBASE_CLIENT_EMAIL')
        self.FIREBASE_CLIENT_ID = os.environ.get('FIREBASE_CLIENT_ID')
        self.FIREBASE_PRIVATE_KEY = os.environ.get('FIREBASE_PRIVATE_KEY')
        self.FIREBASE_PRIVATE_KEY_ID = os.environ.get('FIREBASE_PRIVATE_KEY_ID')
        self.FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')


class Development(Default):
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.SECRET_KEY = os.urandom(24)


class Testing(Default):
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.SECRET_KEY = os.urandom(24)


class Production(Default):
    def __init__(self):
        super().__init__()
        self.DEBUG = False
        self.SECRET_KEY = os.environ['SECRET_KEY']
