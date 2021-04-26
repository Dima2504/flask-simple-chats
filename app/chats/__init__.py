"""Initialization of actually the main chats blueprint."""
from flask import Blueprint

chats = Blueprint('chats', __name__, url_prefix='/chats')

from .models import Message
from .views import UserChatsList

chats.add_url_rule('/list', view_func=UserChatsList.as_view('list'))
