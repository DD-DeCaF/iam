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

import pytest

from iam.app import api
from iam.app import app as app_
from iam.app import init_app
from iam.models import Organization, User
from iam.models import db as db_


@pytest.fixture(scope='session')
def app():
    init_app(app_, api, db_)
    app_.app_context().push()
    return app_


@pytest.fixture(scope='function')
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
