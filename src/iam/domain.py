# Copyright (c) 2018, Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
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

"""Implement domain logic."""

import secrets
from datetime import datetime

from jose import jwt

from .app import app
from .models import User, db


def sign_claims(user):
    """Return signed jwt and refresh token for the given authenticated user."""
    user.refresh_token = secrets.token_hex(32)
    user.refresh_token_expiry = (
        datetime.now() + app.config['REFRESH_TOKEN_VALIDITY'])
    db.session.commit()
    claims = {
        'exp': int((datetime.now() + app.config['JWT_VALIDITY'])
                   .strftime('%s'))
    }
    claims.update(user.claims)
    signed_token = jwt.encode(claims, app.config['RSA_PRIVATE_KEY'],
                              app.config['ALGORITHM'])
    return {
        'jwt': signed_token,
        'refresh_token': {
            'val': user.refresh_token,
            'exp': int(user.refresh_token_expiry.strftime('%s')),
        }
    }


def create_firebase_user(uid, decoded_token):
    """Create a Firebase user from the provided uid and decoded token."""
    if ' ' in decoded_token['name']:
        first_name, last_name = decoded_token['name'].split(None, 1)
    else:
        first_name, last_name = decoded_token['name'], ''

    user = User(
        firebase_uid=uid,
        first_name=first_name,
        last_name=last_name,
        email=decoded_token['email'],
    )
    db.session.add(user)
    db.session.commit()
    return user
