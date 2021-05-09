"""Init flask-restful and a separate blueprint for it"""
from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

from .auth import Register, Token
from .resources.chats import ChatsList, ChatSingle
from .resources.users import UsersList, UserSingle

api.add_resource(Register, '/register', strict_slashes=False)
api.add_resource(Token, '/token', strict_slashes=False)
api.add_resource(ChatsList, '/chats', strict_slashes=False)
api.add_resource(ChatSingle, '/chats/<int:chat_id>', strict_slashes=False)
api.add_resource(UsersList, '/users', strict_slashes=False)
api.add_resource(UserSingle, '/users/<int:user_id>', strict_slashes=False)
