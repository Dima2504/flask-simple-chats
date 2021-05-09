"""Initial module according to the flask factory pattern"""
import os
from .config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
socket_io = SocketIO()
csrf = CSRFProtect()

import app.chats.events


def make_app(test_config: object = None) -> Flask:
    """
    An application factory like in the official documentation.
    Creates and configures the main flask instance registering all the blueprints and additions.
    The function is possible to be used directly by importing and obtaining an application object,
    or by making :envvar:`FLASK_APP` variable be equal to 'app' (only for development).

    :Example:
        $ export FLASK_APP=app
        $ flask run

    :param test_config: can be used to specify special settings for conducting tests.
                        If nothing is put, the function will load a production config if it exists.
    :type test_config: dict; some dict inheritance.
    :returns: a new configured flask application instance.
    :rtype: Flask
    """

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.from_object(test_config)
    else:
        app.config.from_pyfile('production_config.py', silent=True)
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    socket_io.init_app(app)
    csrf.init_app(app)

    from app.views import view
    app.register_blueprint(view)

    from app.commands import cli_commands
    app.register_blueprint(cli_commands)

    from app.authentication import authentication
    app.register_blueprint(authentication)

    from app.chats import chats
    app.register_blueprint(chats)

    return app
