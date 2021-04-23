import functools
from flask import g
from flask import redirect
from flask import url_for
from flask import flash


def login_required(func):
    """Decorator that checks whether the user is logged in or not. If not, it redirects to login page"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if g.user is None:
            flash('You have to log in first')
            return redirect(url_for('authentication.login'))
        return func(*args, **kwargs)
    return wrapper


def anonymous_required(func):
    """Checks whether the user is logged in. If it is so, doesn't allow to visit page"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if g.user:
            flash('You have been already logged in')
            return redirect(url_for('view.index'))
        return func(*args, **kwargs)
    return wrapper