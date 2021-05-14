"""This module supplies with view blueprint. It allows to make up general routs instead of
typical :func:`app.route` in order to work with application factory properly"""
from typing import Tuple

from flask import Blueprint
from flask import render_template
from werkzeug.exceptions import NotFound

from . import logger

view = Blueprint('view', __name__)


@view.route('/')
def index() -> str:
    """
    Handles start page.
    """
    return render_template('index.html')


@view.app_errorhandler(NotFound)
def page_not_found(error: NotFound) -> Tuple[str, int]:
    """
    Handles 404 error.
    """
    logger.info('404 error was raised')
    return render_template('404.html'), error.code
