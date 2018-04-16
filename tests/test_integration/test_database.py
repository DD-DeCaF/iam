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

from iam.models import User


def test_commit(db, models):
    db.session.commit()


def test_owner_role(db, models):
    # Give user owner role, and assign the project to the organization
    models['organization_user'].role = 'owner'
    models['project'].organization = models['organization']
    models['project'].organization_role = 'read'

    # Verify that the user has admin role for the project
    assert models['user'].claims['prj'][models['project'].id] == 'admin'


def test_team_role(db, models):
    # Assign the project to the team with write access
    models['project'].team = models['team']
    models['project'].team_role = 'write'

    # Verify that the user has write role for the project
    assert models['user'].claims['prj'][models['project'].id] == 'write'


def test_user_role(db, models):
    # Assign the project to the user with read access
    models['project'].user = models['user']
    models['project'].user_role = 'read'

    # Verify that the user has write role for the project
    assert models['user'].claims['prj'][models['project'].id] == 'read'
