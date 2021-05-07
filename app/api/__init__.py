"""Init flask-restful and a separate blueprint for it"""
from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

from .auth import Register, Token

api.add_resource(Register, '/register')
api.add_resource(Token, '/token')
