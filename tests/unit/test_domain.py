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

from iam.domain import create_firebase_user
from iam.models import User


def test_create_firebase_user(db):
    user = create_firebase_user('foo_token', {
        'name': 'Foo Bar',
        'email': 'foo@bar.dk',
    })
    assert isinstance(user, User)
    assert user.claims['org'] is None
