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

from datetime import datetime

from firebase_admin import auth
from flask_apispec import MethodResource, doc, marshal_with, use_kwargs
from flask_apispec.extension import FlaskApiSpec
from jose import jwt
from sqlalchemy.orm.exc import NoResultFound

from .app import app
from .domain import create_firebase_user, sign_claims
from .models import Project, User, db
from .schemas import (
    FirebaseCredentialsSchema, JWKKeysSchema, JWTSchema, LocalCredentialsSchema,
    ProjectRequestSchema, ProjectResponseSchema, RefreshRequestSchema,
    TokenSchema)


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
            user = User.query.filter_by(email=email).one()
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
            user = User.query.filter_by(refresh_token=refresh_token).one()
            if datetime.now() >= user.refresh_token_expiry:
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
        return Project.query.all(), 200

    @use_kwargs(ProjectRequestSchema)
    def post(self, name):
        project = Project(name=name)
        db.session.add(project)
        db.session.commit()
        return {'project_id': project.id}, 201


@doc(description="List projects")
class ProjectResource(MethodResource):
    @marshal_with(ProjectResponseSchema(), code=200)
    def get(self, project_id):
        try:
            return Project.query.filter(Project.id == project_id).one(), 200
        except NoResultFound:
            return f"No project with id {project_id}", 404

    @use_kwargs(ProjectRequestSchema)
    def put(self, project_id, name):
        try:
            project = Project.query.filter(Project.id == project_id).one()
        except NoResultFound:
            return f"No project with id {project_id}", 404
        else:
            project.name = name
            db.session.commit()
            return "", 204

    def delete(self, project_id):
        try:
            project = Project.query.filter(Project.id == project_id).one()
        except NoResultFound:
            return f"No project with id {project_id}", 404
        else:
            db.session.delete(project)
            db.session.commit()
            return "", 204


def init_app(app):
    """Register API resources on the provided Flask application."""
    def register(path, resource):
        app.add_url_rule(path, view_func=resource.as_view(resource.__name__))
        docs.register(resource, endpoint=resource.__name__)

    docs = FlaskApiSpec(app)
    register("/authenticate/local", LocalAuthResource)
    register("/authenticate/firebase", FirebaseAuthResource)
    register("/refresh", RefreshResource)
    register("/keys", PublicKeysResource)
    register("/projects", ProjectsResource)
    register("/projects/<project_id>", ProjectResource)
