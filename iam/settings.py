import os


class Default:
    pass


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
