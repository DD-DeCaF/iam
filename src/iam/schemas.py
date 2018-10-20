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

"""Marshmallow schemas for marshalling the API endpoints."""

from marshmallow import Schema, fields


class StrictSchema(Schema):
    class Meta:
        strict = True


# Request schemas
################################################################################

class LocalCredentialsSchema(StrictSchema):
    email = fields.String(required=True, description="Email address")
    password = fields.String(required=True, description="Password")


class FirebaseCredentialsSchema(StrictSchema):
    uid = fields.String(required=True, description="Firebase UID")
    token = fields.String(required=True, description="Firebase token")


class RefreshRequestSchema(StrictSchema):
    refresh_token = fields.String(required=True, description="Refresh token")


class JWTSchema(StrictSchema):
    jwt = fields.String(required=True, description="Signed JWT")


class ProjectRequestSchema(StrictSchema):
    name = fields.String(required=True, description="Project name")
    # TODO:
    # organizations = fields.List(fields.Integer())
    # teams = fields.List(fields.Integer())
    # users = fields.List(fields.Integer())


# Response schemas
################################################################################


class RefreshTokenSchema(StrictSchema):
    val = fields.String(
        required=True,
        description="Refresh token. Use this to request a new JWT when it "
                    "expires")
    exp = fields.Integer(required=True,
                         description="Refresh token expiry (unix time)")


class TokenSchema(StrictSchema):
    jwt = fields.String(required=True, description="Signed JWT")
    refresh_token = fields.Nested(RefreshTokenSchema)


class JWKKeysSchema(StrictSchema):
    class JWKSchema(StrictSchema):
        alg = fields.String()
        e = fields.String()
        n = fields.String()
        kty = fields.String()

    keys = fields.List(
        fields.Nested(JWKSchema),
        description=("List of public keys used for signing.")
    )


class ProjectResponseSchema(StrictSchema):
    id = fields.Integer()
    name = fields.String()
    organizations = fields.List(fields.Integer())
    teams = fields.List(fields.Integer())
    users = fields.List(fields.Integer())
