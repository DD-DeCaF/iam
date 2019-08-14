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

import logging
import os
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from jose import jwt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Mail, Personalization

from . import hasher
from .app import app


db = SQLAlchemy()

logger = logging.getLogger(__name__)


class Organization(db.Model):
    """An Organization."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    teams = db.relationship('Team', back_populates='organization')
    users = db.relationship('OrganizationUser', back_populates='organization')
    projects = db.relationship('OrganizationProject',
                               back_populates='organization')

    def __repr__(self):
        """Return a printable representation."""
        return f"<{self.__class__.__name__} {self.id}: {self.name}>"


class Team(db.Model):
    """A grouping of members within an organization."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'),
                                nullable=False)
    organization = db.relationship('Organization', back_populates='teams')

    users = db.relationship('TeamUser', back_populates='team', lazy='joined')

    projects = db.relationship('TeamProject', back_populates='team')

    def __repr__(self):
        """Return a printable representation."""
        return f"<{self.__class__.__name__} {self.id}: {self.name}>"


class User(db.Model):
    """A User."""

    id = db.Column(db.Integer, primary_key=True)

    # Firebase users will have NULL in the password column.
    password = db.Column(db.String(128))

    firebase_uid = db.Column(db.String(256))

    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    email = db.Column(db.String(256), unique=True, nullable=False)

    organizations = db.relationship('OrganizationUser', back_populates='user',
                                    lazy='joined')
    teams = db.relationship('TeamUser', back_populates='user', lazy='joined')

    projects = db.relationship('UserProject', back_populates='user')

    refresh_tokens = db.relationship('RefreshToken', back_populates='user')

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
            """Add claims, if there is no existing higher claim."""
            if id in project_claims:
                if role == 'read' and project_claims[id] in ('admin', 'write'):
                    return
                if role == 'write' and project_claims[id] == 'admin':
                    return

            project_claims[id] = role

        project_claims = {}

        for user_role in self.organizations:
            if user_role.role == 'owner':
                # Add admin role for all projects in the organization
                for project_role in user_role.organization.projects:
                    add_claim(project_role.project.id, 'admin')

                # Add admin role for all projects in organization teams
                for team in user_role.organization.teams:
                    for team_role in team.projects:
                        add_claim(team_role.project.id, 'admin')
            else:
                # Add the assigned role for all projects in the organization
                for org_role in user_role.organization.projects:
                    add_claim(org_role.project.id, org_role.role)

        # Add the assigned role for all projects in the users' team
        for user_role in self.teams:
            for team_role in user_role.team.projects:
                add_claim(team_role.project.id, team_role.role)

        # Add projects owned by user
        for user_role in self.projects:
            add_claim(user_role.project.id, user_role.role)

        return {'usr': self.id, 'prj': project_claims}

    def get_reset_token(self):
        claims = {
            "exp": (int(datetime.timestamp(datetime.now())) + 3600)
        }
        claims.update(self.claims)
        return jwt.encode(
            claims, app.config["RSA_PRIVATE_KEY"], app.config["ALGORITHM"]
        )

    def send_reset_email(self):
        token = self.get_reset_token()
        try:
            logger.debug(
                f"Sending email with reset link to "
                f"{self.full_name} <{self.email}>"
            )
            sendgrid = SendGridAPIClient()
            mail = Mail()
            mail.from_email = Email("DD-DeCaF <notifications@dd-decaf.eu>")
            mail.template_id = "d-f1addc67e51f4d0e8966d340c24551a4"
            personalization = Personalization()
            personalization.add_to(Email(self.email))
            hosts = {
                "development": "http://localhost:4200",
                "staging": "https://staging.dd-decaf.eu",
                "production": "https://caffeine.dd-decaf.eu"
            }
            personalization.dynamic_template_data = {
                "link":
                    f"{hosts[os.environ['ENVIRONMENT']]}/password-reset/{token}"
            }
            mail.add_personalization(personalization)
            sendgrid.client.mail.send.post(request_body=mail.get())
        except Exception as error:
            # Suppress any problem so it doesn't mark the entire workflow
            # as failed, but do log a warning for potential follow-up.
            logger.warning(
                "Unable to send email with password reset lint", exc_info=error
            )


class RefreshToken(db.Model):
    """A grouping of tokens within an user."""

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64))
    expiry = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

    def __repr__(self):
        """Return a printable representation."""
        return f"<{self.__class__.__name__} {self.token}: " \
               f"{self.expiry}>"


class Project(db.Model):
    """A Project."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    organizations = db.relationship('OrganizationProject',
                                    back_populates='project',
                                    cascade='all, delete-orphan')
    teams = db.relationship('TeamProject', back_populates='project',
                            cascade='all, delete-orphan')
    users = db.relationship('UserProject', back_populates='project',
                            cascade='all, delete-orphan')

    def __repr__(self):
        """Return a printable representation."""
        return f"<{self.__class__.__name__} {self.id}: {self.name}>"


#
# Association tables
#

class OrganizationUser(db.Model):
    """Role for a user belonging to an organization."""

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'),
                                primary_key=True)
    organization = db.relationship('Organization', back_populates='users')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', back_populates='organizations')
    role = db.Column(db.Enum('owner', 'member', name='organization_user_roles'),
                     nullable=False)

    def __repr__(self):
        """Return a printable representation."""
        return (f"<{self.__class__.__name__} {self.role}: {self.user} in "
                f"{self.organization}>")


class TeamUser(db.Model):
    """Role for a user belonging to a team."""

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), primary_key=True)
    team = db.relationship('Team', back_populates='users')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', back_populates='teams')
    role = db.Column(db.Enum('maintainer', 'member', name='team_user_roles'),
                     nullable=False)

    def __repr__(self):
        """Return a printable representation."""
        return (f"<{self.__class__.__name__} {self.role}: {self.user} in "
                f"{self.team}>")


class OrganizationProject(db.Model):
    """Access rule for an organization to a project."""

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'),
                                primary_key=True)
    organization = db.relationship('Organization', back_populates='projects')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'),
                           primary_key=True)
    project = db.relationship('Project', back_populates='organizations')
    role = db.Column(db.Enum('admin', 'write', 'read', name='project_roles'),
                     nullable=False)

    def __repr__(self):
        """Return a printable representation."""
        return (f"<{self.__class__.__name__} {self.organization} has role "
                f"{self.role} in {self.project}>")


class TeamProject(db.Model):
    """Access rule for a team to a project."""

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), primary_key=True)
    team = db.relationship('Team', back_populates='projects')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'),
                           primary_key=True)
    project = db.relationship('Project', back_populates='teams')
    role = db.Column(db.Enum('admin', 'write', 'read', name='project_roles'),
                     nullable=False)

    def __repr__(self):
        """Return a printable representation."""
        return (f"<{self.__class__.__name__} {self.team} has role "
                f"{self.role} in {self.project}>")


class UserProject(db.Model):
    """Access role for a user to a project."""

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', back_populates='projects')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'),
                           primary_key=True)
    project = db.relationship('Project', back_populates='users')
    role = db.Column(db.Enum('admin', 'write', 'read', name='project_roles'),
                     nullable=False)

    def __repr__(self):
        """Return a printable representation."""
        return (f"<{self.__class__.__name__} {self.user} has role "
                f"{self.role} in {self.project}>")
