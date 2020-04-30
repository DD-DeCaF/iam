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

"""Provide settings for different deployment scenarios."""

import os
import pathlib
from datetime import timedelta

from jose import jwk


def current_config():
    """Return the appropriate configuration object based on the environment."""
    if os.environ["ENVIRONMENT"] == "production":
        return Production()
    elif os.environ["ENVIRONMENT"] == "staging":
        return Staging()
    elif os.environ["ENVIRONMENT"] == "testing":
        return Testing()
    elif os.environ["ENVIRONMENT"] == "development":
        return Development()
    else:
        raise KeyError(f"Unknown environment '{os.environ['ENVIRONMENT']}'")


class Default:
    """Default configuration settings."""

    def __init__(self):
        """Initialize the default configuration."""
        self.CORS_ORIGINS = os.environ["ALLOWED_ORIGINS"].split(",")
        self.RSA_PRIVATE_KEY = pathlib.Path("keys/rsa").read_text()
        self.ALGORITHM = "RS512"
        self.RSA_PUBLIC_KEY = (
            jwk.get_key(self.ALGORITHM)(self.RSA_PRIVATE_KEY, self.ALGORITHM,)
            .public_key()
            .to_dict()
        )
        self.JWT_VALIDITY = timedelta(minutes=10)
        self.REFRESH_TOKEN_VALIDITY = timedelta(days=30)
        self.SENTRY_DSN = os.environ.get("SENTRY_DSN")

        self.APISPEC_TITLE = "iam"
        self.APISPEC_SWAGGER_UI_URL = "/"

        self.BASIC_AUTH_USERNAME = os.environ["BASIC_AUTH_USERNAME"]
        self.BASIC_AUTH_PASSWORD = os.environ["BASIC_AUTH_PASSWORD"]

        self.FEAT_TOGGLE_LOCAL_AUTH = bool(os.environ["FEAT_TOGGLE_LOCAL_AUTH"])
        self.SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{os.environ['DB_USERNAME']}:"
            f"{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}:"
            f"{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
            f"?connect_timeout=10"
        )
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

        self.FEAT_TOGGLE_FIREBASE = bool(os.environ["FEAT_TOGGLE_FIREBASE"])
        self.FIREBASE_CLIENT_CERT_URL = os.environ.get(
            "FIREBASE_CLIENT_CERT_URL"
        )
        self.FIREBASE_CLIENT_EMAIL = os.environ.get("FIREBASE_CLIENT_EMAIL")
        self.FIREBASE_CLIENT_ID = os.environ.get("FIREBASE_CLIENT_ID")
        self.FIREBASE_PRIVATE_KEY = os.environ.get("FIREBASE_PRIVATE_KEY")
        self.FIREBASE_PRIVATE_KEY_ID = os.environ.get("FIREBASE_PRIVATE_KEY_ID")
        self.FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID")
        self.SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")

        self.LOGGING = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "simple": {
                    "format": "%(asctime)s [%(levelname)s] [%(name)s] "
                    "%(filename)s:%(funcName)s:%(lineno)d | "
                    "%(message)s"
                },
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "simple",
                },
            },
            "loggers": {
                # All loggers will by default use the root logger below (and
                # hence be very verbose). To silence spammy/uninteresting log
                # output, add the loggers here and increase the loglevel.
                "parso": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": False,
                }
            },
            "root": {"level": "DEBUG", "handlers": ["console"],},
        }


class Development(Default):
    """Development settings."""

    def __init__(self):
        """Initialize the development configuration."""
        super().__init__()
        self.DEBUG = True
        self.SECRET_KEY = os.urandom(24)
        self.ROOT_URL = "http://localhost:4200"


class Testing(Default):
    """Testing settings."""

    def __init__(self):
        """Initialize the testing configuration."""
        super().__init__()
        self.DEBUG = True
        self.SECRET_KEY = os.urandom(24)
        self.TESTING = True
        self.SQLALCHEMY_DATABASE_URI = (
            "postgresql://postgres:@postgres:5432/iam_test"
        )
        self.ROOT_URL = "http://localhost:4200"


class Staging(Default):
    """Staging settings."""

    def __init__(self):
        """Initialize the staging configuration."""
        super().__init__()
        self.DEBUG = False
        self.SECRET_KEY = os.environ["SECRET_KEY"]
        self.LOGGING["root"]["level"] = "INFO"
        self.ROOT_URL = "https://staging.dd-decaf.eu"


class Production(Default):
    """Production settings."""

    def __init__(self):
        """Initialize the production configuration."""
        super().__init__()
        self.DEBUG = False
        self.SECRET_KEY = os.environ["SECRET_KEY"]
        self.LOGGING["root"]["level"] = "INFO"
        self.ROOT_URL = "https://caffeine.dd-decaf.eu"
