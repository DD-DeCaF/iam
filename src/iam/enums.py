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

"""Domain enums."""

from enum import Enum, auto


class EnumBase(Enum):
    def __str__(self):
        """Print `name` instead of `Enum.name`."""
        # Necessary as either SQLAlchemy or Marshmallow casts values of model's
        # Enum fields to values of respective Enum classes. (So it converts
        # "accepted" to ConsentStatus.accepted). But when this value is
        # serialized for request response, by default it gets serialized to
        # "ConsentStatus.accepted" instead of just "accepted"
        return str(self.name)


class ConsentType(EnumBase):
    gdpr = auto()
    cookie = auto()


class ConsentStatus(EnumBase):
    accepted = auto()
    rejected = auto()


# See https://gdpr.eu/cookies/ > Types of Cookies > Purpose
class CookieConsentCategory(EnumBase):
    strictly_necessary = auto()
    preferences = auto()
    statistics = auto()
    marketing = auto()
