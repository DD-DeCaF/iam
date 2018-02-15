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

    # note: a project should belong to an organization or user, but not both
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    organization = db.relationship('Organization',
                                   backref=db.backref('projects'))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('projects'))

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}: {self.name}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    password = db.Column(db.String(128))
    refresh_token = db.Column(db.String(64))
    refresh_token_expiry = db.Column(db.DateTime)

    firebase_uid = db.Column(db.String(256))

    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
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

    @property
    def claims(self):
        return {
            'org': self.organization_id,
            'prj': list({p.id for p in self.organization.projects}.union(
                {p.id for p in self.projects})),
        }
