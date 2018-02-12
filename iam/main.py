from flask import Flask

from . import settings


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings.Settings)
    return app
