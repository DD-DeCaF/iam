import base64
import json
from datetime import datetime

import pytest
from jose import jwt

from iam.app import create_app
from iam.models import Organization, Project, User
from iam.models import db as db_


@pytest.fixture
def app():
    app = create_app()
    app.app_context().push()
    return app


@pytest.fixture
def db():
    db_.create_all()
    yield db_
    db_.session.remove()
    db_.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(db):
    user = User(first_name='Foo', last_name='Bar', email='foo@bar.dk',
                organization=Organization(name='FooOrg'))
    password = 'hunter2'
    user.set_password(password)
    db.session.add(user)
    return (user, password)


def test_get_admin_unauthorized(client):
    rv = client.get('/admin/')
    assert rv.status_code == 401


def test_get_admin_authorized(client, app):
    credentials = base64.b64encode(f'{app.config["BASIC_AUTH_USERNAME"]}:'
                                   f'{app.config["BASIC_AUTH_PASSWORD"]}'
                                   .encode()).decode()
    rv = client.get('/admin/',
                    headers={'Authorization': f'Basic {credentials}'})
    assert rv.status_code == 200


def test_db(db):
    organization = Organization(name='FooOrg')
    project = Project(name='FooProject', organization=organization)
    user = User(first_name='Foo', last_name='Bar', email='foo@bar.dk',
                organization=organization)
    user.set_password('hunter2')
    db.session.add(organization)
    db.session.add(project)
    db.session.add(user)
    db.session.commit()


def test_authenticate_failure(app, client, db, user):
    user, password = user
    response = client.post('/authenticate')
    assert response.status_code == 400

    response = client.post('/authenticate', data={
        'email': user.email,
        'password': 'invalid',
    })
    assert response.status_code == 401


def test_authenticate_success(app, client, user):
    user, password = user
    response = client.post('/authenticate', data={
        'email': user.email,
        'password': password,
    })
    assert response.status_code == 200
    data_decoded = json.loads(response.data)
    raw_jwt_token = data_decoded['jwt']
    refresh_token = data_decoded['refresh_token']

    # Decode the provided JWT with the public key from the service endpoint
    keys = json.loads(client.get('/keys').data)
    key = keys['keys'][0]
    returned_claims = jwt.decode(raw_jwt_token, key, app.config['ALGORITHM'])
    assert user.organization_id == returned_claims['org']

    # Check the refresh token
    assert len(user.refresh_token) == 64
    assert user.refresh_token == refresh_token['val']
    assert user.refresh_token_expiry > datetime.now()
    assert user.refresh_token_expiry < (datetime.now() +
                                        app.config['REFRESH_TOKEN_VALIDITY'])

    # Attempt to refresh token
    response = client.post('/refresh',
                           data={'refresh_token': refresh_token['val']})
    assert response.status_code == 200
    refresh_claims = jwt.decode(response.data, key, app.config['ALGORITHM'])
    assert refresh_claims == returned_claims
