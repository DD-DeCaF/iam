from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate

from . import settings
from .models import Organization, Project, User, db


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings.Settings)

    Migrate(app, db)
    db.init_app(app)

    admin = Admin(app, template_mode='bootstrap3')
    admin.add_view(ModelView(Organization, db.session))
    admin.add_view(ModelView(Project, db.session))
    admin.add_view(ModelView(User, db.session))

    return app


app = create_app()
