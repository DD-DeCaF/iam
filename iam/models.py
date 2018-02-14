from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}: {self.name}>'


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship('Organization', backref=db.backref('projects', lazy=True))

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}: {self.name}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), nullable=False)

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship('Organization', backref=db.backref('users', lazy=True))

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}: {self.full_name} ({self.email})>'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
