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

import getpass
import logging

import click
import firebase_admin
from firebase_admin import credentials
from flask import Flask, jsonify, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_basicauth import BasicAuth
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restplus import Api
from raven.contrib.flask import Sentry
from sqlalchemy.orm.exc import NoResultFound

from . import settings
from .models import Organization, Project, User


app = Flask(__name__)
api = Api(
    title="IAM API",
    version="0.0.1",
    description="Identity and access management",
)


def init_app(application, interface, db):
    from . import resources

    application.config.from_object(settings.Settings)

    Migrate(application, db)
    db.init_app(application)

    if application.config['SENTRY_DSN']:
        sentry = Sentry(dsn=application.config['SENTRY_DSN'], logging=True,
                        level=logging.WARNING)
        sentry.init_app(application)

    CORS(application)

    if application.config['FEAT_TOGGLE_FIREBASE']:
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

    # ADMIN VIEWS
    ############################################################################

    admin = Admin(application, template_mode='bootstrap3',
                  url=f"{application.config['SERVICE_URL']}/admin")
    admin.add_view(ModelView(Organization, db.session))
    admin.add_view(ModelView(Project, db.session))
    admin.add_view(ModelView(User, db.session))

    # Require basic authentication for admin views
    basic_auth = BasicAuth(application)

    @application.before_request
    def restrict_admin():
        if request.path.startswith(admin.url) and not basic_auth.authenticate():
            return basic_auth.challenge()

    # API RESOURCES
    ############################################################################

    interface.add_resource(resources.AuthenticateLocal,
                           f"{application.config['SERVICE_URL']}"
                           f"/authenticate/local")
    interface.add_resource(resources.AuthenticateFirebase,
                           f"{application.config['SERVICE_URL']}"
                           f"/authenticate/firebase")
    interface.add_resource(resources.Refresh,
                           f"{application.config['SERVICE_URL']}/refresh")
    interface.add_resource(resources.PublicKeys,
                           f"{application.config['SERVICE_URL']}/keys")
    interface.init_app(application)

    @application.route(f"{application.config['SERVICE_URL']}/openapi.json")
    def openapi_schema():
        return jsonify(api.__schema__)

    # CLI COMMANDS
    ############################################################################

    @application.cli.command()
    def users():
        """List all users"""
        for user in User.query.all():
            print(user)

    @application.cli.command()
    @click.argument('id')
    def set_password(id):
        """Set a users password. (Run 'users' to see all user ids)"""
        try:
            user = User.query.filter_by(id=id).one()
            print(f"Updating password for: {user}")
            password = getpass.getpass()
            user.set_password(password)
            db.session.commit()
        except NoResultFound:
            print(f"No user has id {id} (try `flask users`)")
