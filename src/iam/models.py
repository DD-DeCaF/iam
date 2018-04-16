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

"""Data models."""

from flask_sqlalchemy import SQLAlchemy

from . import hasher


db = SQLAlchemy()

class Organization(db.Model):
    """An Organization."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    teams = db.relationship('Team', back_populates='organization')
    users = db.relationship('OrganizationUser', back_populates='organization')
    projects = db.relationship('Project', back_populates='organization')

    def __repr__(self):
        """Return a printable representation."""
        return f"<{self.__class__.__name__} {self.id}: {self.name}>"


class OrganizationUser(db.Model):
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'),
                                primary_key=True)
    organization = db.relationship('Organization', back_populates='users')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', back_populates='organizations')
    role = db.Column(db.Enum('owner', 'member', name='organization_user_roles'),
                     nullable=False)

    def __repr__(self):
        return (f"<{self.__class__.__name__} {self.role}: {self.user} in "
                f"{self.organization}>")


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'),
                                nullable=False)
    organization = db.relationship('Organization', back_populates='teams')

    users = db.relationship('TeamUser', back_populates='team', lazy='joined')

    projects = db.relationship('Project', back_populates='team')

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}: {self.name}>"


class TeamUser(db.Model):
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), primary_key=True)
    team = db.relationship('Team', back_populates='users')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', back_populates='teams')
    role = db.Column(db.Enum('maintainer', 'member', name='team_user_roles'),
                     nullable=False)

    def __repr__(self):
        return (f"<{self.__class__.__name__} {self.role}: {self.user} in "
                f"{self.team}>")

class User(db.Model):
    """A User."""

    id = db.Column(db.Integer, primary_key=True)

    password = db.Column(db.String(128))
    refresh_token = db.Column(db.String(64))
    refresh_token_expiry = db.Column(db.DateTime)

    firebase_uid = db.Column(db.String(256))

    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    email = db.Column(db.String(256), unique=True, nullable=False)

    organizations = db.relationship('OrganizationUser', back_populates='user',
                                   lazy='joined')
    teams = db.relationship('TeamUser', back_populates='user', lazy='joined')

    projects = db.relationship('Project', back_populates='user')

    def __repr__(self):
        """Return a printable representation."""
        return (f"<{self.__class__.__name__} {self.id}: {self.full_name} "
                f"({self.email})>")

    @property
    def full_name(self):
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}"

    def set_password(self, password):
        """Encode and set the given password."""
        if not password:
            raise ValueError("Password cannot be empty")
        self.password = hasher.encode(password)

    def check_password(self, password):
        """Return true if the given password matches the users' password."""
        return hasher.verify(password, self.password)

    @property
    def claims(self):
        """Return this users' claims for use in a JWT."""
        def add_claim(id, role):
            """Add claims, if there are no existing higher claim"""
            if id in project_claims:
                if role == 'read' and project_claims[id] in ('admin', 'write'):
                    return
                if role == 'write' and project_claims[id] == 'admin':
                    return

            project_claims[id] = role

        project_claims = {}

        for org_role in self.organizations:
            if org_role.role == 'owner':
                # Add admin role for all projects in the organization
                for project in org_role.organization.projects:
                    add_claim(project.id, 'admin')

                # Add admin role for all projects in organization teams
                for team in org_role.organization.teams:
                    for project in team.projects:
                        add_claim(project.id, 'admin')
            else:
                # Add the assigned role for all projects in the organization
                for project in org_role.organization.projects:
                    add_claim(project.id, project.organization_role)

        # Add the assigned role for all projects in the users' team
        for team_role in self.teams:
            for project in team_role.team.projects:
                add_claim(project.id, project.team_role)

        # Add projects owned by user
        for project in self.projects:
            add_claim(project.id, project.user_role)

        return {'prj': project_claims}


class Project(db.Model):
    """A Project."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    # note: a project must belong to *either* an organization, a team or a
    # user
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    organization = db.relationship('Organization',
                                   back_populates='projects')
    organization_role = db.Column(db.Enum('admin', 'write', 'read',
                                          name='project_roles'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team = db.relationship('Team', back_populates='projects')
    team_role = db.Column(db.Enum('admin', 'write', 'read',
                                          name='project_roles'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='projects')
    user_role = db.Column(db.Enum('admin', 'write', 'read',
                                          name='project_roles'))

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}: {self.name}>"
