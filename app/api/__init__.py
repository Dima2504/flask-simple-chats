"""Init flask-restful and a separate blueprint for it"""
import logging

from flask import Blueprint
from flask_restful import Api

from app import csrf

api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)
csrf.exempt(api_bp)
logger = logging.getLogger(__name__)
logger.info('Api blueprint is being loaded')


from .auth import Register, Token, Update, ForgotPassword, ResetPassword
from .resources.chats import ChatsList, ChatSingle
from .resources.users import UsersList, UserSingle
from .resources.messages import ChatMessagesList, ChatMessageSingle

api.add_resource(Register, '/register', strict_slashes=False)
api.add_resource(Token, '/token', strict_slashes=False)
api.add_resource(Update, '/update', strict_slashes=False)
api.add_resource(ForgotPassword, '/forgot-password', strict_slashes=False)
api.add_resource(ResetPassword, '/reset-password', strict_slashes=False)

api.add_resource(ChatsList, '/chats', strict_slashes=False)
api.add_resource(ChatSingle, '/chats/<int:chat_id>', strict_slashes=False)
api.add_resource(ChatMessagesList, '/chats/<int:chat_id>/messages', strict_slashes=False)
api.add_resource(ChatMessageSingle, '/chats/<int:chat_id>/messages/<int:message_id>', strict_slashes=False)

api.add_resource(UsersList, '/users', strict_slashes=False)
api.add_resource(UserSingle, '/users/<int:user_id>', strict_slashes=False)
