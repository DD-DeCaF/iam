from flask import Flask

from iam import main


def test_main():
    assert isinstance(main.create_app(), Flask)
