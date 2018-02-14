import base64

import pytest

from iam import main


@pytest.fixture
def client():
    return main.app.test_client()


@pytest.fixture
def app():
    return main.app


def test_get_admin_unauthorized(client):
    rv = client.get('/admin/')
    assert rv.status_code == 401


def test_get_admin_authorized(client, app):
    credentials = base64.b64encode(f'{app.config["BASIC_AUTH_USERNAME"]}:{app.config["BASIC_AUTH_PASSWORD"]}'.encode()).decode()
    rv = client.get('/admin/', headers={'Authorization': f'Basic {credentials}'})
    assert rv.status_code == 200
