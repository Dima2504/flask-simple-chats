"""Init authentication blueprint which starts from host:port/authentication/"""
from flask import Blueprint
from flask import g

authentication = Blueprint('authentication', __name__, url_prefix='/authentication')


@authentication.app_context_processor
def insert_user():
    """Adds variable `user` into a context of each template. if it is not None, the current user has logged in.
    If it is None, the current user is anonymous"""
    return {'user': g.user}


from .models import User
from .views import LoginView, RegisterView, ForgotPasswordView, ResetPasswordView

authentication.add_url_rule('/login', view_func=LoginView.as_view('login'))
authentication.add_url_rule('/register', view_func=RegisterView.as_view('register'))
authentication.add_url_rule('/forgot_password', view_func=ForgotPasswordView.as_view('forgot_password'))
authentication.add_url_rule('/reset_password/<string:token>', view_func=ResetPasswordView.as_view('reset_password'))
