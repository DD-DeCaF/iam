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

from marshmallow import Schema, ValidationError, fields, validates_schema

from .validators import (
    validate_consent_category, validate_consent_status, validate_consent_type)


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


class ConsentRegisterSchema(StrictSchema):
    type = fields.String(
        required=True,
        validate=lambda val: validate_consent_type(val, ValidationError))
    category = fields.String(required=True)
    status = fields.String(
        required=True,
        validate=lambda val: validate_consent_status(val, ValidationError))
    timestamp = fields.DateTime()
    valid_until = fields.DateTime()
    message = fields.String()
    source = fields.String()

    @validates_schema
    def validate_category(self, data, **kwargs):
        return validate_consent_category(data, data['category'],
                                         errtype=ValidationError)


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
    # TODO:
    # organizations = fields.List(fields.Integer())
    # teams = fields.List(fields.Integer())
    # users = fields.List(fields.Integer())


class UserResponseSchema(StrictSchema):
    id = fields.Integer()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.String()


class UserRegisterSchema(StrictSchema):
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    email = fields.String(required=True)
    password = fields.String(required=True)


class ResetRequestSchema(StrictSchema):
    email = fields.String(required=True)


class PasswordResetSchema(StrictSchema):
    token = fields.String(location="query")
    password = fields.String(location="json")


class ConsentResponseSchema(StrictSchema):
    type = fields.String(
        required=True,
        validate=lambda val: validate_consent_type(val, ValidationError),
        description="Type of the consent, e.g. GDPR or cookie consent")
    category = fields.String(
        required=True,
        description="Category the consent relates to.")
    status = fields.String(
        required=True,
        validate=lambda val: validate_consent_status(val, ValidationError),
        description="Whether the consent was accepted or rejected.")
    timestamp = fields.DateTime(
        required=True,
        description="Time of when user responded to the consent")
    valid_until = fields.DateTime(
        description="Time of when the consent should be revoked. Null implies "
                    "unlimited validity")
    message = fields.String(description="Exact wording of what the user "
                                        "consented to.")
    source = fields.String(description="Source of the consent.")

    @validates_schema
    def validate_category(self, data, **kwargs):
        validate_consent_category(data, data['category'],
                                  errtype=ValidationError)
