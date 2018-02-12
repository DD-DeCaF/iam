import os


class Default:
    POSTGRES_USERNAME = os.environ['POSTGRES_USERNAME']
    POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
    POSTGRES_HOST = os.environ['POSTGRES_HOST']
    POSTGRES_PORT = os.environ['POSTGRES_PORT']
    POSTGRES_DATABASE = os.environ['POSTGRES_DATABASE']
    SQLALCHEMY_DATABASE_URI = ('postgres://{}:{}@{}:{}/{}'.format(
                                POSTGRES_USERNAME, POSTGRES_PASSWORD,
                                POSTGRES_HOST, POSTGRES_PORT,
                                POSTGRES_DATABASE))
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Development(Default):
    DEBUG = True
    SECRET_KEY = os.urandom(24)


class Production(Default):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')


if os.environ['CONFIGURATION'] == 'prod':
    Settings = Production
    assert Settings.SECRET_KEY
else:
    Settings = Development
