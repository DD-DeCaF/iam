# Copyright 2018 Novo Nordisk Foundation Center for Biosustainability, DTU.
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

"""Unit tests for the hasher module."""

from iam import hasher


def test_encode():
    """Test encoding password with various parameters."""
    assert hasher.verify('foo', hasher.encode('foo'))
    assert hasher.verify('foo', hasher.encode('foo', iterations=50))
    assert hasher.verify('foo', hasher.encode('foo', salt='bar', iterations=50))
    assert not hasher.verify('foo', hasher.encode('bar', iterations=50))

    assert hasher.encode('foo', iterations=99) != hasher.encode('foo',
                                                                iterations=100)


def test_str_bytes():
    """Test that verification is str/bytes agnostic."""
    password_str = 'æøå'
    password_bytes = password_str.encode()
    iterations = 50  # for faster tests
    assert hasher.verify(password_str, hasher.encode(password_str,
                                                     iterations=iterations))
    assert hasher.verify(password_bytes, hasher.encode(password_str,
                                                       iterations=iterations))
    assert hasher.verify(password_str, hasher.encode(password_bytes,
                                                     iterations=iterations))
    assert hasher.verify(password_bytes, hasher.encode(password_bytes,
                                                       iterations=iterations))
