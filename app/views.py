"""This module supplies with view blueprint. It allows to make up general routs instead of
typical :func:`app.route` in order to work with application factory properly"""
from flask import render_template
from flask import Blueprint
from werkzeug.exceptions import NotFound
from typing import Tuple

view = Blueprint('view', __name__)


@view.route('/')
def index() -> str:
    """
    Handles start page.
    """
    return render_template('index.html')


@view.app_errorhandler(NotFound)
def page_not_found(e: NotFound) -> Tuple[str, int]:
    """
    Handles 404 error.
    """
    return render_template('404.html'), 404
