from iam import hasher


def test_encode():
    assert hasher.verify('foo', hasher.encode('foo'))
    assert hasher.verify('foo', hasher.encode('foo', iterations=50))
    assert hasher.verify('foo', hasher.encode('foo', salt='bar', iterations=50))
    assert not hasher.verify('foo', hasher.encode('bar', iterations=50))

    assert (hasher.encode('foo', iterations=99) !=
            hasher.encode('foo', iterations=100))


def test_str_bytes():
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
