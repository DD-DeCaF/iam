# Copyright (c) 2018, Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum
from operator import getitem

from .enums import ConsentStatus, ConsentType, CookieConsentCategory


def validate_consent_type(value, errtype=None):
    errtype = errtype or Exception
    if isinstance(value, Enum):
        value = value.name
    try:
        ConsentType[value]
    except KeyError:
        raise errtype(
            'Invalid consent type "{0}". Type must be one '
            'of {1}.'.format(
                value,
                [c.name for c in ConsentType]
            ))
    return value


def validate_consent_status(value, errtype=None):
    errtype = errtype or Exception
    if isinstance(value, Enum):
        value = value.name
    try:
        ConsentStatus[value]
    except KeyError:
        raise errtype(
            'Invalid consent status "{0}". Status must be one '
            'of {1}.'.format(
                value,
                [c.name for c in ConsentStatus]
            ))
    return value


def validate_consent_category(obj, value, errtype=None, accessor=None):
    accessor = accessor or getitem
    errtype = errtype or Exception
    # If this validator is used for data returned through Marshmallow's schema,
    # the process removes invalid fields from the response. This leads to
    # the accessor raising an exception if it can't find the field.
    # The following try/except covers such event for standard accessors
    # (getitem, getattr).
    # User-defined accessors should handle errors by returning None.
    # (catching all exceptions would not be appropriate if case user-defined
    # logic would have other errors)
    # For more info, this occurs in marshmallow(2.x).schema.py:_do_load
    try:
        consent_type = accessor(obj, 'type')
    except (KeyError, AttributeError):
        # Field 'type' has been removed from the response, so the data has
        # already been validated and failed. No need to validate it again.
        return value
    if isinstance(consent_type, Enum):
        consent_type = consent_type.name
    if consent_type == ConsentType.cookie.name:
        try:
            CookieConsentCategory[value]
        except KeyError:
            raise errtype(
                'Invalid cookie consent category "{0}". Category must be one '
                'of {1}.'.format(
                    value,
                    [c.name for c in CookieConsentCategory]
                ))
    return value
