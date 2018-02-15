import getpass

import click
from flask import Flask, abort, jsonify, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_basicauth import BasicAuth
from flask_migrate import Migrate
from jose import jwk, jwt
from sqlalchemy.orm.exc import NoResultFound

from . import settings
from .models import Organization, Project, User, db


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings.Settings)

    Migrate(app, db)
    db.init_app(app)

    # ADMIN VIEWS
    ############################################################################

    admin = Admin(app, template_mode='bootstrap3')
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

    @app.route('/authenticate', methods=['POST'])
    def auth():
        try:
            email = request.form['email'].strip()
            password = request.form['password'].strip()
            user = User.query.filter_by(email=email).one()
            if user.check_password(password):
                # Authenticated, return the JWT
                claims = {
                    'org': user.organization_id,
                    'prj': [p.id for p in user.organization.projects],
                }
                return jwt.encode(claims, app.config['RSA_PRIVATE_KEY'],
                                  app.config['ALGORITHM'])
            else:
                abort(401)
        except NoResultFound:
            abort(401)

    @app.route('/keys')
    def public_key():
        key = jwk.get_key(app.config['ALGORITHM'])(app.config['RSA_PUBLIC_KEY'],
                                                   app.config['ALGORITHM'])
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
