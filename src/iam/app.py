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

"""Expose the main Flask application."""

import getpass
import logging
import logging.config

import click
import firebase_admin
from firebase_admin import credentials
from flask import Flask, jsonify, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_basicauth import BasicAuth
from flask_cors import CORS
from flask_migrate import Migrate
from raven.contrib.flask import Sentry
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.contrib.fixers import ProxyFix

from . import errorhandlers, jwt, resources
from .models import (
    Organization, OrganizationProject, OrganizationUser, Project, RefreshToken,
    Team, TeamProject, TeamUser, User, UserProject)
from .settings import current_config


logger = logging.getLogger(__name__)
app = Flask(__name__)


def init_app(application, db):
    """Initialize the main app with config information and routes."""
    application.config.from_object(current_config())

    # Configure logging
    logging.config.dictConfig(application.config['LOGGING'])

    logger.info("Logging configured")

    logger.debug("Initializing database")
    Migrate(application, db)
    db.init_app(application)

    logger.debug("Initializing sentry")
    if application.config['SENTRY_DSN']:
        sentry = Sentry(dsn=application.config['SENTRY_DSN'], logging=True,
                        level=logging.ERROR)
        sentry.init_app(application)

    logger.debug("Initializing CORS")
    CORS(application)

    if application.config['FEAT_TOGGLE_FIREBASE']:
        logger.info("Initializing Firebase")
        cred = credentials.Certificate({
            'type': 'service_account',
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://accounts.google.com/o/oauth2/token',
            'auth_provider_x509_cert_url':
                'https://www.googleapis.com/oauth2/v1/certs',
            'project_id': application.config['FIREBASE_PROJECT_ID'],
            'private_key_id': application.config['FIREBASE_PRIVATE_KEY_ID'],
            'private_key': application.config['FIREBASE_PRIVATE_KEY'],
            'client_email': application.config['FIREBASE_CLIENT_EMAIL'],
            'client_id': application.config['FIREBASE_CLIENT_ID'],
            'client_x509_cert_url':
                application.config['FIREBASE_CLIENT_CERT_URL'],
        })
        firebase_admin.initialize_app(cred)
    else:
        logger.info("Firebase feature toggle is off")

    # Add JWT middleware
    ############################################################################
    jwt.init_app(application)

    # ADMIN VIEWS
    ############################################################################

    logger.debug("Registering admin views")
    admin = Admin(application, template_mode='bootstrap3',
                  url=f"/admin")
    admin.add_view(ModelView(Organization, db.session))
    admin.add_view(ModelView(Team, db.session))
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Project, db.session))
    admin.add_view(ModelView(OrganizationUser, db.session))
    admin.add_view(ModelView(TeamUser, db.session))
    admin.add_view(ModelView(OrganizationProject, db.session))
    admin.add_view(ModelView(TeamProject, db.session))
    admin.add_view(ModelView(UserProject, db.session))
    admin.add_view(ModelView(RefreshToken, db.session))

    # Require basic authentication for admin views
    basic_auth = BasicAuth(application)

    @application.before_request
    def restrict_admin():
        if request.path.startswith(admin.url) and not basic_auth.authenticate():
            return basic_auth.challenge()

    # Add routes and resources.
    resources.init_app(application)

    # Register error handlers.
    errorhandlers.init_app(application)

    # CLI COMMANDS
    ############################################################################

    logger.debug("Registering CLI commands")

    @application.cli.command()
    def users():
        """List all users."""
        for user in User.query.all():
            print(user)

    @application.cli.command()
    @click.argument('id')
    def set_password(id):
        """Set a users password. (Run 'users' to see all user ids)."""
        try:
            user = User.query.filter_by(id=id).one()
            print(f"Updating password for: {user}")
            password = getpass.getpass()
            user.set_password(password)
            db.session.commit()
        except NoResultFound:
            print(f"No user has id {id} (try `flask users`)")

    # Please keep in mind that it is a security issue to use such a middleware
    # in a non-proxy setup because it will blindly trust the incoming headers
    # which might be forged by malicious clients.
    # We require this in order to serve the HTML version of the OpenAPI docs
    # via https.
    application.wsgi_app = ProxyFix(application.wsgi_app)

    logger.info("App initialization complete")
