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
from jose import jwt

from iam.app import app as app_
from iam.app import init_app
from iam.enums import ConsentStatus, ConsentType, CookieConsentCategory
from iam.models import Consent, Organization, Project, Team, User
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
    """Drop and recreate all tables in the database."""
    # Ensure no sessions are left in an open state, which may happen if tests
    # not using a db session run before setting up tests that do.
    db_.session.close()
    db_.drop_all()
    db_.create_all()


@pytest.fixture(scope="session")
def db_fixtures(db_tables):
    """
    Provide default preinstalled db fixtures.

    These are installed session-wide and shared for performance reasons, but
    tests may of course create their own encapsulated test data if needed.
    """
    organization = Organization(name='OrgName')
    team = Team(name='TeamName', organization=organization)
    user = User(first_name='User', last_name='Name', email='user@name.test')
    user.set_password('hunter2')
    user2 = User(first_name='User2', last_name='Name2', email='user2@name.test')
    user2.set_password('hunter2')
    project = Project(name='ProjectName')

    # user1 consent
    consent = Consent(type=ConsentType.cookie.name,
                      category=CookieConsentCategory.statistics.name,
                      status=ConsentStatus.accepted.name,
                      user=user)
    # This consent has the same category and type, and is created more
    # recently, so on request, this consent should be returned instead.
    consent_override = Consent(type=ConsentType.cookie.name,
                               category=CookieConsentCategory.statistics.name,
                               status=ConsentStatus.rejected.name,
                               user=user)
    # This consent has the same category and type, and is created more
    # recently, but is associated with another user, so on user1's request,
    # this consent should not be returned.
    consent_conflict = Consent(type=ConsentType.cookie.name,
                               category=CookieConsentCategory.statistics.name,
                               status=ConsentStatus.accepted.name,
                               user=user2)

    db_.session.add(organization)
    db_.session.add(team)
    db_.session.add_all([user, user2])
    db_.session.add(project)
    db_.session.add_all([consent, consent_override, consent_conflict])
    db_.session.commit()


@pytest.fixture(scope="session")
def connection():
    """Establish a distinct db connection to be able to use transactions."""
    with db_.engine.connect() as connection:
        yield connection


@pytest.fixture(scope="function")
def session(db_tables, connection):
    """
    Provide a database test session.

    Wraps the session in a transaction which is rolled back at the end of the
    test, undoing any operations committed in the session.

    The session is closed upon completion and the original Flask-SQLAlchemy
    session is reset on the db object.

    See also:
    https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#session-external-transaction

    """
    # Keep a reference to the original session in order to reset it for
    # subsequent tests that may not require a DB session.
    flask_sqlalchemy_session = db_.session

    # Create a new scoped session, bound to an external transaction which can be
    # rolled back independently of the session state.
    transaction = connection.begin()
    db_.session = db_.create_scoped_session(
        options={'bind': connection, 'binds': {}})
    yield db_.session

    # Roll back anything that occurred in the test session and reset the db
    # session to the original flask-sqlalchemy session.
    db_.session.close()
    transaction.rollback()
    db_.session = flask_sqlalchemy_session


@pytest.fixture(scope="function")
def models(db_fixtures, session):
    """Provide preinstalled db fixtures queried from the current db session."""
    return {
        'organization': Organization.query.one(),
        'team': Team.query.one(),
        'user': User.query.all(),
        'project': Project.query.one(),
        'consent': Consent.query.all()
    }


@pytest.fixture(scope="session")
def tokens(app):
    """Provide user 1 with read, write and admin JWT claims to project 1."""
    return {
        'read': jwt.encode(
            {
                'usr': 1,
                'prj': {1: 'read'}
            },
            app.config['RSA_PRIVATE_KEY'],
            app.config['ALGORITHM'],
        ),
        'write': jwt.encode(
            {
                'usr': 1,
                'prj': {1: 'write'}
            },
            app.config['RSA_PRIVATE_KEY'],
            app.config['ALGORITHM'],
        ),
        'admin': jwt.encode(
            {
                'usr': 1,
                'prj': {1: 'admin'}
            },
            app.config['RSA_PRIVATE_KEY'],
            app.config['ALGORITHM'],
        ),
    }
