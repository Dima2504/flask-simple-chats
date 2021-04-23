"""Init authentication blueprint which starts from host:port/authentication/"""
from flask import Blueprint

authentication = Blueprint('authentication', __name__, url_prefix='/authentication')

from .models import User
from .views import LoginView, RegisterView, ForgotPasswordView, ResetPasswordView

authentication.add_url_rule('/login', view_func=LoginView.as_view('login'))
authentication.add_url_rule('/register', view_func=RegisterView.as_view('register'))
authentication.add_url_rule('/forgot_password', view_func=ForgotPasswordView.as_view('forgot_password'))
authentication.add_url_rule('/reset_password/<string:token>', view_func=ResetPasswordView.as_view('reset_password'))
