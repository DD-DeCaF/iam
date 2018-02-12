from flask import Flask

from iam import main


def test_main():
    assert isinstance(main.app, Flask)
