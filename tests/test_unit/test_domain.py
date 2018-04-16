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

"""Unit tests for the domain module."""

from datetime import datetime

from iam.domain import create_firebase_user, sign_claims
from iam.models import User


def test_sign_claims(app, models):
    """Test the sign_claims function."""
    claims = sign_claims(models['user'])
    assert len(claims['jwt']) > 0
    assert len(claims['refresh_token']['val']) > 0
    expiry = datetime.fromtimestamp(claims['refresh_token']['exp'])
    assert datetime.now() < expiry
    assert datetime.now() + app.config['REFRESH_TOKEN_VALIDITY'] >= expiry


def test_create_firebase_user(db):
    """Test creating a Firebase user."""
    user = create_firebase_user('foo_token', {
        'name': 'Foo Bar',
        'email': 'foo@bar.dk',
    })
    assert isinstance(user, User)
    assert len(user.claims['prj'].keys()) == 0
