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

"""Provide session level fixtures."""

import pytest

from iam.app import app as app_
from iam.app import init_app
from iam.models import Organization, Project, Team, User
from iam.models import db as db_


@pytest.fixture(scope="session")
def app():
    """Provide an initialized Flask for use in certain test cases."""
    init_app(app_, db_)
    with app_.app_context():
        yield app_


@pytest.fixture(scope="session")
def client(app):
    """Provide a Flask test client for endpoint integration tests."""
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="session")
def db_tables(app):
    """Provide a database session with tables created."""
    db_.create_all()
    yield db_
    db_.drop_all()


@pytest.fixture(scope="function")
def db(db_tables):
    """Provide a database session in a transaction rolled back on completion."""
    db_tables.session.begin_nested()
    yield db_tables
    db_tables.session.rollback()


@pytest.fixture(scope="function")
def models(db):
    """Return a fixture with test data for all data models."""
    organization = Organization(name='OrgName')
    team = Team(name='TeamName', organization=organization)
    user = User(first_name='User', last_name='Name', email='user@name.test')
    user.set_password('hunter2')
    project = Project(name='ProjectName')
    models = {
        'organization': organization,
        'team': team,
        'user': user,
        'project': project,
    }
    for model in models.values():
        db.session.add(model)
    return models
