from flask_sqlalchemy import SQLAlchemy

from . import hasher


db = SQLAlchemy()


class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}: {self.name}>'


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'),
                                nullable=False)
    organization = db.relationship('Organization',
                                   backref=db.backref('projects'))

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}: {self.name}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    password = db.Column(db.String(128), nullable=False)

    first_name = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'),
                                nullable=False)
    organization = db.relationship('Organization', backref=db.backref('users'))

    def __repr__(self):
        return (f'<{self.__class__.__name__} {self.id}: {self.full_name} '
                f'({self.email})>')

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def set_password(self, password):
        if not password:
            raise ValueError("Password cannot be empty")
        self.password = hasher.encode(password)

    def check_password(self, password):
        return hasher.verify(password, self.password)
