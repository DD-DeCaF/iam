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

"""Tests for the database integration."""

from iam.models import (
    OrganizationProject, OrganizationUser, TeamProject, TeamUser, UserProject)


def test_owner_role(session, models):
    """Test a users admin access to a project through the organization."""
    user = models['user'][0]
    # Give user owner role, and assign the project to the organization
    OrganizationUser(organization=models['organization'], user=user,
                     role='owner')
    OrganizationProject(organization=models['organization'],
                        project=models['project'], role='read')

    # Verify that the user has admin role for the project
    assert user.claims['prj'][models['project'].id] == 'admin'


def test_team_role(session, models):
    """Test a users access to a project through a team."""
    user = models['user'][0]
    # Assign the user to the team, and give the team write access to the project
    TeamUser(team=models['team'], user=user, role='member')
    TeamProject(team=models['team'], project=models['project'], role='write')

    # Verify that the user has write role for the project
    assert user.claims['prj'][models['project'].id] == 'write'


def test_user_role(session, models):
    """Test a users direct access to a project."""
    user = models['user'][0]
    # Assign the user to the project with read access
    UserProject(user=user, project=models['project'], role='read')

    # Verify that the user has write role for the project
    assert user.claims['prj'][models['project'].id] == 'read'
