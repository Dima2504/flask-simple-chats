"""Init authentication blueprint which starts from host:port/authentication/"""
from flask import Blueprint

authentication = Blueprint('authentication', __name__, url_prefix='authentication')

from .models import User
