"""Initialization of actually the main chats blueprint."""
from flask import Blueprint

chats = Blueprint('chats', __name__, url_prefix='/chats')

from .models import Message
