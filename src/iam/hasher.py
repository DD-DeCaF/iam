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

"""Password hasher."""

import base64
import hashlib
import hmac
import secrets
import string


def new_salt(n=12):
    """Generate a new salt."""
    salt_chars = string.ascii_letters + string.digits
    salt = [secrets.choice(salt_chars) for _ in range(n)]
    return "".join(salt)


def encode(password, salt=None, iterations=100000):
    """Encode the given password."""
    if salt is None:
        salt = new_salt()
    if not isinstance(password, bytes):
        password = password.encode()
    hash = hashlib.pbkdf2_hmac(
        hashlib.sha256().name, password, salt.encode(), iterations, None
    )
    hash = base64.b64encode(hash).decode("ascii").strip()
    return "{:d}${}${}".format(iterations, salt, hash)


def verify(password, encoded):
    """Return True if the given password matches the given encoded password."""
    if not isinstance(password, bytes):
        password = password.encode()
    iterations, salt, hash = encoded.split("$", 2)
    encoded_new = encode(password, salt, int(iterations))
    return hmac.compare_digest(encoded.encode(), encoded_new.encode())
