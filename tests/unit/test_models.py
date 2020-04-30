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

"""Unit tests for the models module."""

import pytest
from jose import jwt
from sqlalchemy.exc import DataError

from iam.models import Consent, db


def test_reset_token(app, models):
    """Test the get_reset_token method."""
    user = models["user"][0]
    encoded_token = user.get_reset_token()
    decoded_token = jwt.decode(
        encoded_token, app.config["RSA_PRIVATE_KEY"], app.config["ALGORITHM"]
    )
    assert decoded_token["usr"] == user.id


@pytest.mark.parametrize(
    "input",
    [
        # cookie consent
        {"type": "cookie", "category": "statistics", "status": "accepted"},
        # gdpr consent
        {"type": "gdpr", "category": "newsletter", "status": "rejected",},
    ],
)
def test_create_consent(models, input):
    user = models["user"][0]
    consent = Consent(**input, user=user)
    assert consent


def test_create_consent_fail_on_invalid_type(models):
    user = models["user"][0]
    with pytest.raises(DataError):
        consent = Consent(
            category="performance", type="wookie", status="accepted", user=user
        )
        db.session.add(consent)
        db.session.commit()


@pytest.mark.parametrize(
    "input",
    [
        # invalid reject status
        {"type": "gdpr", "category": "newsletter", "status": "rej",},
        # invalid accept status
        {"type": "cookie", "category": "statistics", "status": "akceptted",},
    ],
)
def test_create_consent_fail_on_invalid_status(models, input):
    user = models["user"][0]
    with pytest.raises(DataError):
        consent = Consent(**input, user=user)
        db.session.add(consent)
        db.session.commit()
