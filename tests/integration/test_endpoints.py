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

"""Test integrations like API resources and the database layer."""

import base64
import json
from datetime import datetime, timedelta

from jose import jwt


def test_openapi_schema(app, client):
    """Test OpenAPI schema resource."""
    response = client.get('/swagger/')
    assert response.status_code == 200
    assert len(json.loads(response.data)['paths']) > 0


def test_healthz(client):
    """Test the readiness endpoint."""
    response = client.get('/healthz')
    assert response.status_code == 200


def test_metrics(client, db):
    """Test the metrics endpoint."""
    response = client.get('/metrics')
    assert response.status_code == 200


def test_get_admin_unauthorized(client):
    """Test unauthorized access to the admin view."""
    rv = client.get('/admin/')
    assert rv.status_code == 401


def test_get_admin_authorized(client, app):
    """Test authorized access to the admin view."""
    credentials = base64.b64encode(f'{app.config["BASIC_AUTH_USERNAME"]}:'
                                   f'{app.config["BASIC_AUTH_PASSWORD"]}'
                                   .encode()).decode()
    rv = client.get('/admin/',
                    headers={'Authorization': f'Basic {credentials}'})
    assert rv.status_code == 200


def test_authenticate_failure(app, client, models):
    """Test invalid local authentication."""
    response = client.post('/authenticate/local')
    assert response.status_code == 422

    response = client.post('/authenticate/local', data={
        'email': models['user'].email,
        'password': 'invalid',
    })
    assert response.status_code == 401


def test_authenticate_success(app, client, db, models):
    """Test valid local authentication."""
    response = client.post('/authenticate/local', data={
        'email': models['user'].email,
        'password': 'hunter2',
    })
    assert response.status_code == 200
    data_decoded = json.loads(response.data)
    raw_jwt_token = data_decoded['jwt']
    refresh_token = data_decoded['refresh_token']

    # Decode the provided JWT with the public key from the service endpoint
    keys = json.loads(client.get('/keys').data)
    key = keys['keys'][0]
    returned_claims = jwt.decode(raw_jwt_token, key, app.config['ALGORITHM'])
    del returned_claims['exp']
    assert models['user'].claims == returned_claims

    # Check the refresh token
    assert len(models['user'].refresh_token) == 64
    assert models['user'].refresh_token == refresh_token['val']
    assert models['user'].refresh_token_expiry > datetime.now()
    assert models['user'].refresh_token_expiry < (
        datetime.now() + app.config['REFRESH_TOKEN_VALIDITY'])

    # Attempt to refresh token
    response = client.post('/refresh',
                           data={'refresh_token': refresh_token['val']})
    assert response.status_code == 200
    raw_jwt_token = json.loads(response.data)['jwt']
    refresh_claims = jwt.decode(raw_jwt_token, key, app.config['ALGORITHM'])
    # Assert that the claims are equal, but not the expiry, which will have
    # refreshed
    del refresh_claims['exp']
    assert refresh_claims == returned_claims

    models['user'].refresh_token_expiry = datetime.now() - timedelta(seconds=1)
    response = client.post('/refresh',
                           data={'refresh_token': models['user'].refresh_token})
    assert response.status_code == 401
