import pytest
from flask import Flask

from iam import app
from iam.models import User
from iam.models import db as db_


@pytest.fixture
def db():
    db_.create_all()
    yield db_
    db_.session.remove()
    db_.drop_all()


def test_app():
    assert isinstance(app.create_app(), Flask)


def test_create_firebase_user(db):
    user = app.create_firebase_user('foo_token', {
        'name': 'Foo Bar',
        'email': 'foo@bar.dk',
    })
    assert isinstance(user, User)
    assert user.claims['org'] is None
