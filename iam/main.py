from flask import Flask
from flask_migrate import Migrate

from . import settings
from .models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings.Settings)
    Migrate(app, db)
    db.init_app(app)
    return app


app = create_app()
