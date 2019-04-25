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

from iam.models import Project, User


def test_openapi_schema(app, client):
    """Test OpenAPI schema resource."""
    response = client.get('/swagger/')
    assert response.status_code == 200
    assert len(json.loads(response.data)['paths']) > 0


def test_healthz(client):
    """Test the readiness endpoint."""
    response = client.get('/healthz')
    assert response.status_code == 200


def test_metrics(client):
    """Test the metrics endpoint."""
    response = client.get('/metrics')
    assert response.status_code == 200


def test_get_admin_unauthorized(client):
    """Test unauthorized access to the admin view."""
    response = client.get('/admin/')
    assert response.status_code == 401


def test_get_admin_authorized(app, client):
    """Test authorized access to the admin view."""
    credentials = base64.b64encode(f'{app.config["BASIC_AUTH_USERNAME"]}:'
                                   f'{app.config["BASIC_AUTH_PASSWORD"]}'
                                   .encode()).decode()
    response = client.get('/admin/',
                          headers={'Authorization': f'Basic {credentials}'})
    assert response.status_code == 200


def test_authenticate_failure(app, client, models):
    """Test invalid local authentication."""
    response = client.post('/authenticate/local')
    assert response.status_code == 422

    response = client.post('/authenticate/local', data={
        'email': models['user'].email,
        'password': 'invalid',
    })
    assert response.status_code == 401


def test_authenticate_success(app, client, session, models):
    """Test valid local authentication."""
    response = client.post('/authenticate/local', data={
        'email': models['user'].email,
        'password': 'hunter2',
    })
    assert response.status_code == 200
    raw_jwt_token = json.loads(response.data)['jwt']

    returned_claims = jwt.decode(
        raw_jwt_token,
        app.config['RSA_PUBLIC_KEY'],
        app.config['ALGORITHM'],
    )
    del returned_claims['exp']
    assert models['user'].claims == returned_claims


def test_authenticate_refresh(app, client, session, models):
    """Test the token refresh endpoint."""
    # Authenticate to receive a refresh token
    response = client.post('/authenticate/local', data={
        'email': models['user'].email,
        'password': 'hunter2',
    })
    refresh_token = json.loads(response.data)['refresh_token']

    # Check that token values are as expected
    assert len(refresh_token['val']) == 64
    assert datetime.fromtimestamp(refresh_token['exp']) > datetime.now()
    assert datetime.fromtimestamp(refresh_token['exp']) < (
        datetime.now() + app.config['REFRESH_TOKEN_VALIDITY'])

    # Check that the returned token is now stored in the database
    assert refresh_token['val'] == \
        models['user'].refresh_tokens[0].token

    # Expect refreshing token to succeed
    response = client.post('/refresh',
                           data={'refresh_token': refresh_token['val']})
    assert response.status_code == 200
    raw_jwt_token = json.loads(response.data)['jwt']

    # Expect that the new claims are equal to the user claims, except for the
    # expiry which will have refreshed
    refresh_claims = jwt.decode(
        raw_jwt_token,
        app.config['RSA_PUBLIC_KEY'],
        app.config['ALGORITHM'],
    )
    del refresh_claims['exp']
    assert models['user'].claims == refresh_claims

    # Expect refreshing an expired token to fail
    token = models['user'].refresh_tokens[0]
    token.expiry = datetime.now() - timedelta(seconds=1)
    response = client.post('/refresh', data={'refresh_token': token.token})
    assert response.status_code == 401


def test_create_project(client, session, tokens):
    """Create a new project."""
    response = client.post("/projects", json={
        'name': "New Project",
        'organizations': [],
        'teams': [],
        'users': [],
    }, headers={
        'Authorization': f"Bearer {tokens['write']}",
    })
    assert response.status_code == 201
    project_id = response.json['id']
    assert Project.query.filter(Project.id == project_id).count() == 1


def test_get_projects(client, session, models, tokens):
    """Retrieve list of models."""
    response = client.get("/projects", headers={
        'Authorization': f"Bearer {tokens['read']}",
    })
    assert response.status_code == 200
    assert len(response.json) > 0


def test_get_project(client, session, models, tokens):
    """Retrieve single models."""
    response = client.get(f"/projects/{models['project'].id}", headers={
        'Authorization': f"Bearer {tokens['read']}",
    })
    assert response.status_code == 200
    assert response.json['name'] == "ProjectName"


def test_put_project(client, session, models, tokens):
    """Retrieve single models."""
    response = client.put(f"/projects/{models['project'].id}", json={
        'name': "Changed",
        'organizations': [],
        'teams': [],
        'users': [],
    }, headers={
        'Authorization': f"Bearer {tokens['write']}",
    })
    assert response.status_code == 204
    project = Project.query.filter(Project.id == models['project'].id).one()
    assert project.name == "Changed"


def test_delete_project(client, session, models, tokens):
    """Delete a project."""
    response = client.delete(f"/projects/{models['project'].id}", headers={
        'Authorization': f"Bearer {tokens['admin']}",
    })
    assert response.status_code == 204
    assert Project.query.filter(Project.id == 1).count() == 0


def test_keys(app, client):
    """Retrieve public key from the /keys endpoint."""
    response = client.get("/keys")
    assert response.status_code == 200
    assert len(response.json['keys']) > 0


def test_user(app, client, session, models, tokens):
    """Retrieve user data based on given token."""
    response = client.get("/user", headers={
        'Authorization': f"Bearer {tokens['read']}",
    })
    assert response.status_code == 200

    # Verify returned data against the database
    user_id = jwt.decode(
        tokens['read'],
        app.config['RSA_PUBLIC_KEY'],
        app.config['ALGORITHM'],
    )['usr']
    user = User.query.filter(User.id == user_id).one()
    assert user.first_name == response.json['first_name']
    assert user.last_name == response.json['last_name']
    assert user.email == response.json['email']


def test_user_no_jwt(client):
    """Attempt to get user data with no token."""
    response = client.get("/user")
    assert response.status_code == 401
