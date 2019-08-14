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

from iam.models import User


def test_reset_token(app, models):
    """Test the get_reset_token method"""
    user = models["user"]
    encoded_token = user.get_reset_token()
    decoded_token = jwt.decode(
        encoded_token, app.config["RSA_PRIVATE_KEY"], app.config["ALGORITHM"]
    )
    assert decoded_token["usr"] == user.id
