import base64
import hashlib
import hmac
import secrets
import string


def new_salt(n=12):
    salt_chars = string.ascii_letters + string.digits
    salt = [secrets.choice(salt_chars) for _ in range(n)]
    return ''.join(salt)


def encode(password, salt=None, iterations=100000):
    if salt is None:
        salt = new_salt()
    if not isinstance(password, bytes):
        password = password.encode()
    hash = hashlib.pbkdf2_hmac(hashlib.sha256().name, password, salt.encode(),
                               iterations, None)
    hash = base64.b64encode(hash).decode('ascii').strip()
    return "{:d}${}${}".format(iterations, salt, hash)


def verify(password, encoded):
    if not isinstance(password, bytes):
        password = password.encode()
    iterations, salt, hash = encoded.split('$', 2)
    encoded_new = encode(password, salt, int(iterations))
    return hmac.compare_digest(encoded.encode(), encoded_new.encode())
