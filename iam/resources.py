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

"""IAM API endpoints"""

from datetime import datetime

from firebase_admin import auth
from flask import abort, request
from flask_restplus import Resource, fields
from jose import jwk, jwt
from sqlalchemy.orm.exc import NoResultFound

from .app import api, app, create_firebase_user, sign_claims
from .models import User


json_web_token = api.model("JSON Web Token", {
    'jwt': fields.String(required=True),
})

token_set = api.model("JWT and refresh token", {
    'jwt': fields.String(required=True),
    'refresh_token': fields.Nested(api.model("Refresh Token", {
        'val': fields.String(required=True),
        'exp': fields.Integer(required=True),
    })),
})

json_web_keys = api.model("JSON Web Keys", {
    'keys': fields.List(fields.Nested(api.model("JSON Web Key", {
        'alg': fields.String,
        'e': fields.String,
        'n': fields.String,
        'kty': fields.String,
    })))
})


class AuthenticateLocal(Resource):
    @api.marshal_with(token_set)
    def post(self):
        if not app.config['FEAT_TOGGLE_LOCAL_AUTH']:
            return abort(501, "Local user authentication is disabled")

        try:
            email = request.form['email'].strip()
            password = request.form['password'].strip()
            user = User.query.filter_by(email=email).one()
            if user.check_password(password):
                return sign_claims(user)
            else:
                return abort(401, "Invalid credentials")
        except NoResultFound:
            return abort(401, "Invalid credentials")


class AuthenticateFirebase(Resource):
    @api.marshal_with(token_set)
    def post(self):
        if not app.config['FEAT_TOGGLE_FIREBASE']:
            return abort(501, "Firebase authentication is disabled")

        try:
            uid = request.form['uid'].strip()
            token = request.form['token'].strip()
            decoded_token = auth.verify_id_token(token)
        except ValueError:
            return abort(401, "Invalid firebase credentials")

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


class Refresh(Resource):
    @api.marshal_with(json_web_token)
    def post(self):
        try:
            user = User.query.filter_by(
                refresh_token=request.form['refresh_token']).one()
            if datetime.now() >= user.refresh_token_expiry:
                return abort(401,
                             "The refresh token has expired, please"
                             "re-authenticate")

            claims = {
                'exp': int((datetime.now() + app.config['JWT_VALIDITY'])
                           .strftime('%s'))
            }
            claims.update(user.claims)
            return {'jwt': jwt.encode(claims,
                                      app.config['RSA_PRIVATE_KEY'],
                                      app.config['ALGORITHM'])}
        except NoResultFound:
            return abort(401, "Invalid refresh token")


class PublicKeys(Resource):
    @api.marshal_with(json_web_keys)
    def get(self):
        key = jwk.get_key(app.config['ALGORITHM'])(
            app.config['RSA_PRIVATE_KEY'],
            app.config['ALGORITHM'])
        public_key = key.public_key().to_dict()
        # python-jose outputs exponent and modulus as bytes
        public_key['e'] = public_key['e'].decode()
        public_key['n'] = public_key['n'].decode()
        return {'keys': [public_key]}
