from iam import main
from flask import Flask


def test_main():
    assert isinstance(main.create_app(), Flask)
