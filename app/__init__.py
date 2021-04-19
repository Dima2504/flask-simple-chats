"""Initial module according to the flask factory pattern"""
from flask import Flask


def make_app(test_config: dict = None) -> Flask:
    """
    An application factory like in the official documentation.
    Creates and configures the main flask instance registering all the blueprints and additions.
    The function is possible to be used directly by importing and obtaining an application object,
    or by making FLASK_APP variable be equal to 'app' (only for development).

    :Example:
        $ export FLASK_APP=app
        $ flask run

    :param test_config: can be used to specify special settings for conducting tests.
                        If nothing is put, the function will load a normal config.
    :type test_config: dict, some dict inheritance.
    :returns: a new configured Flask application instance.
    :rtype: Flask
    """

    app = Flask(__name__)

    return app
