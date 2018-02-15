import getpass
import logging
import secrets
from datetime import datetime

import click
from firebase_admin import auth
from flask import Flask, abort, jsonify, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_basicauth import BasicAuth
from flask_migrate import Migrate
from jose import jwk, jwt
from raven.contrib.flask import Sentry
from sqlalchemy.orm.exc import NoResultFound

from . import settings
from .models import Organization, Project, User, db


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings.Settings)

    Migrate(app, db)
    db.init_app(app)

    sentry = Sentry(dsn=app.config['SENTRY_DSN'], logging=True,
                    level=logging.WARNING)
    sentry.init_app(app)

    # ADMIN VIEWS
    ############################################################################

    admin = Admin(app, template_mode='bootstrap3',
                  url=f"{app.config['SERVICE_URL']}/admin")
    admin.add_view(ModelView(Organization, db.session))
    admin.add_view(ModelView(Project, db.session))
    admin.add_view(ModelView(User, db.session))

    # Require basic authentication for admin views
    basic_auth = BasicAuth(app)

    @app.before_request
    def restrict_admin():
        if request.path.startswith(admin.url) and not basic_auth.authenticate():
            return basic_auth.challenge()

    # HANDLERS
    ############################################################################

    @app.route(f"{app.config['SERVICE_URL']}/authenticate/local",
               methods=['POST'])
    def auth_local():
        try:
            email = request.form['email'].strip()
            password = request.form['password'].strip()
            user = User.query.filter_by(email=email).one()
            if user.check_password(password):
                payload = sign_claims(app, user)
                return jsonify(payload)
            else:
                abort(401)
        except NoResultFound:
            abort(401)

    @app.route(f"{app.config['SERVICE_URL']}/authenticate/firebase",
               methods=['POST'])
    def auth_firebase():
        try:
            uid = request.form['uid'].strip()
            token = request.form['token'].strip()
            decoded_token = auth.verify_id_token(token)
            if 'email' not in decoded_token:
                decoded_token['email'] = (
                    auth.get_user(uid).provider_data[0].email)
            try:
                user = User.query.filter_by(firebase_uid=uid).one()
            except NoResultFound:
                try:
                    # no firebase user for this provider, but they may have
                    # signed up with a different provider but the same email
                    user = User.query.filter_by(email=decoded_token['email'])
                except NoResultFound:
                    # no such user - create a new one
                    user = create_firebase_user(uid, decoded_token)

            payload = sign_claims(app, user)
            return jsonify(payload)
        except NoResultFound:
            abort(401)

    @app.route(f"{app.config['SERVICE_URL']}/refresh", methods=['POST'])
    def refresh():
        try:
            user = User.query.filter_by(
                refresh_token=request.form['refresh_token']).one()
            if datetime.now() >= user.refresh_token_expiry:
                response = jsonify({'error': "The refresh token has expired, "
                                    "please re-authenticate."})
                response.status_code = 401
                return response

            claims = {
                'exp': int((datetime.now() + app.config['JWT_VALIDITY'])
                           .strftime('%s'))
            }
            claims.update(user.claims)
            return jwt.encode(claims, app.config['RSA_PRIVATE_KEY'],
                              app.config['ALGORITHM'])
        except NoResultFound:
            abort(404)

    @app.route(f"{app.config['SERVICE_URL']}/keys")
    def public_key():
        key = jwk.get_key(app.config['ALGORITHM'])(
            app.config['RSA_PRIVATE_KEY'], app.config['ALGORITHM'])
        public_key = key.public_key().to_dict()
        # python-jose outputs exponent and modulus as bytes
        public_key['e'] = public_key['e'].decode()
        public_key['n'] = public_key['n'].decode()
        return jsonify({'keys': [public_key]})

    # CLI COMMANDS
    ############################################################################

    @app.cli.command()
    def users():
        """List all users"""
        for user in User.query.all():
            print(user)

    @app.cli.command()
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

    return app


def sign_claims(app, user):
    """return signed jwt and refresh token for the given authenticated user"""
    user.refresh_token = secrets.token_hex(32)
    user.refresh_token_expiry = (
        datetime.now() + app.config['REFRESH_TOKEN_VALIDITY'])
    db.session.commit()
    claims = {
        'exp': int((datetime.now() + app.config['JWT_VALIDITY'])
                   .strftime('%s'))
    }
    claims.update(user.claims)
    signed_token = jwt.encode(claims, app.config['RSA_PRIVATE_KEY'],
                              app.config['ALGORITHM'])
    return {
        'jwt': signed_token,
        'refresh_token': {
            'val': user.refresh_token,
            'exp': int(user.refresh_token_expiry.strftime('%s')),
        }
    }


def create_firebase_user(uid, decoded_token):
    if ' ' in decoded_token['name']:
        first_name, last_name = decoded_token['name'].split(None, 1)
    else:
        first_name, last_name = decoded_token['name'], ''

    user = User(
        firebase_uid=uid,
        first_name=first_name,
        last_name=last_name,
        email=decoded_token['email'],
    )
    db.session.add(user)
    db.session.commit()
    return user
