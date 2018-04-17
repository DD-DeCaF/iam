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

    def __repr__(self):
        """Return a printable representation."""
        return f'<{self.__class__.__name__} {self.id}: {self.name}>'


class Project(db.Model):
    """A Project."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    # note: a project should belong to an organization or user, but not both
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    organization = db.relationship('Organization',
                                   backref=db.backref('projects'))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('projects'))

    def __repr__(self):
        """Return a printable representation."""
        return f'<{self.__class__.__name__} {self.id}: {self.name}>'


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

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    organization = db.relationship('Organization', backref=db.backref('users'))

    def __repr__(self):
        """Return a printable representation."""
        return (f'<{self.__class__.__name__} {self.id}: {self.full_name} '
                f'({self.email})>')

    @property
    def full_name(self):
        """Return the full name of the user."""
        return f'{self.first_name} {self.last_name}'

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
        projects = {p.id for p in self.projects}
        if self.organization_id is not None:
            projects = projects.union({
                p.id for p in self.organization.projects})
        return {
            'org': self.organization_id,
            'prj': list(projects),
        }
