from flask import Flask

from iam import app


def test_app():
    assert isinstance(app.create_app(), Flask)
