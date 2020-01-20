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

"""Implement RESTful API endpoints using resources."""

import os
import warnings
from datetime import datetime

import prometheus_client
from firebase_admin import auth
from flask import Response, g, jsonify
from flask_apispec import MethodResource, doc, marshal_with, use_kwargs
from flask_apispec.extension import FlaskApiSpec
from jose import jwt
from sqlalchemy import and_, func
from sqlalchemy.orm.exc import NoResultFound

from .app import app
from .domain import create_firebase_user, sign_claims
from .jwt import jwt_require_claim, jwt_required
from .metrics import ORGANIZATION_COUNT, PROJECT_COUNT, USER_COUNT
from .models import (
    Consent, Organization, Project, RefreshToken, User, UserProject, db)
from .schemas import (
    ConsentRegisterSchema, ConsentResponseSchema, FirebaseCredentialsSchema,
    JWKKeysSchema, JWTSchema, LocalCredentialsSchema, PasswordResetSchema,
    ProjectRequestSchema, ProjectResponseSchema, RefreshRequestSchema,
    ResetRequestSchema, TokenSchema, UserRegisterSchema, UserResponseSchema)


def init_app(app):
    """Register API resources on the provided Flask application."""
    def register(path, resource):
        app.add_url_rule(path, view_func=resource.as_view(resource.__name__))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            docs.register(resource, endpoint=resource.__name__)

    docs = FlaskApiSpec(app)
    app.add_url_rule('/healthz', healthz.__name__, healthz)
    app.add_url_rule('/metrics', metrics.__name__, metrics)
    register("/authenticate/local", LocalAuthResource)
    register("/authenticate/firebase", FirebaseAuthResource)
    register("/refresh", RefreshResource)
    register("/keys", PublicKeysResource)
    register("/projects", ProjectsResource)
    register("/projects/<project_id>", ProjectResource)
    register("/user", UserResource)
    register("/user", UserRegisterResource)
    register("/consent", ConsentResource)
    register("/password/reset-request", ResetRequestResource)
    register("/password/reset/<token>", PasswordResetResource)


def healthz():
    """
    Run readiness checks.

    Failed checks are allowed to raise uncaught exceptions to be logged.
    """
    checks = []

    # Database ping
    db.session.execute('select version()').fetchall()
    checks.append({'name': "DB Connectivity", 'status': 'pass'})

    return jsonify(checks)


def metrics():
    """Expose metrics to prometheus."""
    # Update persistent metrics like database counts
    labels = ('iam', os.environ['ENVIRONMENT'])
    USER_COUNT.labels(*labels).set(User.query.count())
    ORGANIZATION_COUNT.labels(*labels).set(Organization.query.count())
    PROJECT_COUNT.labels(*labels).set(Project.query.count())

    return Response(prometheus_client.generate_latest(),
                    mimetype=prometheus_client.CONTENT_TYPE_LATEST)


@doc(description="Authenticate with email credentials")
class LocalAuthResource(MethodResource):
    """Authenticate with credentials in the local database."""

    @use_kwargs(LocalCredentialsSchema)
    @marshal_with(TokenSchema, code=200)
    def post(self, email, password):
        """Authenticate with credentials in the local database."""
        if not app.config['FEAT_TOGGLE_LOCAL_AUTH']:
            return "Local user authentication is disabled", 501

        try:
            user = User.query.filter(
                User.email == email,
                User.password.isnot(None),
            ).one()
            if user.check_password(password):
                return sign_claims(user)
            else:
                return "Invalid credentials", 401
        except NoResultFound:
            return "Invalid credentials", 401


@doc(description="Authenticate with firebase credentials")
class FirebaseAuthResource(MethodResource):
    """Authenticate with Firebase uid and token."""

    @use_kwargs(FirebaseCredentialsSchema)
    @marshal_with(TokenSchema, code=200)
    def post(self, uid, token):
        """Authenticate with Firebase uid and token."""
        if not app.config['FEAT_TOGGLE_FIREBASE']:
            return "Firebase authentication is disabled", 501

        try:
            decoded_token = auth.verify_id_token(token)
        except ValueError:
            return "Invalid firebase credentials", 401

        if 'email' not in decoded_token:
            decoded_token['email'] = (
                auth.get_user(uid).provider_data[0].email)
        try:
            user = User.query.filter_by(firebase_uid=uid).one()

        except NoResultFound:
            try:
                # no firebase user for this provider, but they may have
                # signed up with a different provider but the same email
                user = User.query.filter_by(email=decoded_token['email']).one()
            except NoResultFound:
                # no such user - create a new one
                user = create_firebase_user(uid, decoded_token)

        return sign_claims(user)


@doc(description="Refresh an expired JWT with a refresh token")
class RefreshResource(MethodResource):
    """Receive a fresh JWT by providing a valid refresh token."""

    @use_kwargs(RefreshRequestSchema)
    @marshal_with(JWTSchema, code=200)
    def post(self, refresh_token):
        """Receive a fresh JWT by providing a valid refresh token."""
        try:
            token = RefreshToken.query.filter_by(token=refresh_token).one()
            user = User.query.filter_by(id=token.user_id).one()
            if datetime.now() >= token.expiry:
                return ("The refresh token has expired, please re-authenticate",
                        401)

            claims = {
                'exp': int((datetime.now() + app.config['JWT_VALIDITY'])
                           .strftime('%s'))
            }
            claims.update(user.claims)
            return {'jwt': jwt.encode(claims,
                                      app.config['RSA_PRIVATE_KEY'],
                                      app.config['ALGORITHM'])}
        except NoResultFound:
            return "Invalid refresh token", 401


@doc(description="""List of public keys used for JWT signing.
See [RFC 7517](https://tools.ietf.org/html/rfc7517) or [the OpenID Connect
implementation](https://connect2id.com/products/server/docs/api/jwk-set#keys)"""
     )
class PublicKeysResource(MethodResource):
    @marshal_with(JWKKeysSchema, code=200)
    def get(self):
        return {'keys': [app.config['RSA_PUBLIC_KEY']]}


@doc(description="List projects")
class ProjectsResource(MethodResource):
    @marshal_with(ProjectResponseSchema(many=True), code=200)
    def get(self):
        return Project.query.filter(Project.id.in_(g.jwt_claims['prj'])), 200

    @use_kwargs(ProjectRequestSchema)
    @jwt_required
    def post(self, name):
        user = User.query.filter(User.id == g.jwt_claims['usr']).one()
        project = Project(name=name)
        user_project = UserProject(
            user=user,
            project=project,
            role='admin',
        )
        db.session.add(project)
        db.session.add(user_project)
        db.session.commit()
        return {'id': project.id}, 201


@doc(description="List projects")
class ProjectResource(MethodResource):
    @marshal_with(ProjectResponseSchema(), code=200)
    def get(self, project_id):
        try:
            return Project.query.filter(
                Project.id == project_id,
                Project.id.in_(g.jwt_claims['prj'])
            ).one(), 200
        except NoResultFound:
            return f"No project with id {project_id}", 404

    @use_kwargs(ProjectRequestSchema)
    @jwt_required
    def put(self, project_id, name):
        try:
            project = Project.query.filter(
                Project.id == project_id,
                Project.id.in_(g.jwt_claims['prj'])
            ).one()
        except NoResultFound:
            return f"No project with id {project_id}", 404
        else:
            jwt_require_claim(project.id, 'write')
            project.name = name
            db.session.commit()
            return "", 204

    @jwt_required
    def delete(self, project_id):
        try:
            project = Project.query.filter(
                Project.id == project_id,
                Project.id.in_(g.jwt_claims['prj'])
            ).one()
        except NoResultFound:
            return f"No project with id {project_id}", 404
        else:
            jwt_require_claim(project.id, 'admin')
            db.session.delete(project)
            db.session.commit()
            return "", 204


@doc(description="Retrieve user data for the user claim in the provided JWT")
class UserResource(MethodResource):
    @marshal_with(UserResponseSchema(), code=200)
    @jwt_required
    def get(self):
        try:
            return User.query.filter(User.id == g.jwt_claims['usr']).one(), 200
        except NoResultFound:
            return f"No user with id {g.jwt_claims['usr']}", 404


@doc(description="Register a user and authenticate in the local database")
class UserRegisterResource(MethodResource):
    @use_kwargs(UserRegisterSchema)
    def post(self, first_name, last_name, email, password):
        # Check if specified email already exists
        exists = db.session.query(User.id).filter_by(email=email).scalar()
        if exists:
            return f"User with provided email already exists", 400

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return sign_claims(user)


@doc(description="Retrieve and submit user consents for the user claim in the "
                 "provided JWT")
class ConsentResource(MethodResource):
    @marshal_with(ConsentResponseSchema(many=True), code=200)
    @jwt_required
    def get(self):
        try:
            # Select the latest user's consents for all unique combinations
            # of consent.type and consent.category
            # Query adapted from https://stackoverflow.com/questions/40537934
            subquery = db.session.query(
                Consent.user_id.label("user_id"),
                Consent.type.label("type"),
                Consent.category.label("category"),
                func.max(Consent.timestamp).label("latest_timestamp")
            ).group_by(
                Consent.user_id,
                Consent.type,
                Consent.category,
            ).subquery()
            query = db.session.query(Consent).join(
                subquery,
                and_(
                    Consent.user_id == g.jwt_claims['usr'],
                    Consent.type == subquery.c.type,
                    Consent.category == subquery.c.category,
                    Consent.timestamp == subquery.c.latest_timestamp,
                )
            ).order_by(
                Consent.type,
                Consent.category
            )
            return query, 200
        except NoResultFound:
            return f"No user with id {g.jwt_claims['usr']}", 404

    @use_kwargs(ConsentRegisterSchema)
    @jwt_required
    def post(self, type, category, status, timestamp=None, valid_until=None,
             message=None, source=None):
        consent = Consent(
            type=type,
            category=category,
            status=status,
            timestamp=timestamp if timestamp is not None else datetime.now(),
            user_id=g.jwt_claims['usr'],
            valid_until=valid_until,
            message=message,
            source=source
        )
        db.session.add(consent)
        db.session.commit()
        return {'id': consent.id}, 201


@doc(description="Request password reset link")
class ResetRequestResource(MethodResource):
    @use_kwargs(ResetRequestSchema)
    def post(self, email):
        user = User.query.filter_by(email=email).first()
        if not user:
            return (
                "There is no account with the provided email. "
                "You must register first.",
                404,
            )
        if user.firebase_uid:
            return (
                "You cannot change password to your social account.",
                404,
            )
        return user.send_reset_email()


@doc(description="Password reset")
class PasswordResetResource(MethodResource):
    def get(self, token):
        try:
            jwt.decode(
                token, app.config["RSA_PRIVATE_KEY"], app.config["ALGORITHM"]
            )
            return "", 200
        except (jwt.JWTError, jwt.ExpiredSignatureError, jwt.JWTClaimsError):
            return "The token is invalid or expired.", 400

    @use_kwargs(PasswordResetSchema)
    def post(self, token, password):
        try:
            decoded_token = jwt.decode(
                token, app.config["RSA_PRIVATE_KEY"], app.config["ALGORITHM"]
            )
        except (jwt.JWTError, jwt.ExpiredSignatureError, jwt.JWTClaimsError):
            return "The token is invalid or expired.", 400
        else:
            user_id = decoded_token["usr"]
            user = User.query.filter_by(id=user_id).first()
            user.set_password(password)
            db.session.commit()
            return "", 200
