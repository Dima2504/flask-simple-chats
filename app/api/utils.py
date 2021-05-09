from sqlalchemy.engine.row import Row
from app.authentication.models import User, chats
from app.authentication.exceptions import UserNotFoundByIndexError
from flask_restful import abort
from app import db


def return_chat_or_abort(chat_id: int) -> Row:
    """Returns chat instance with given id. If it does not exist - makes abort."""
    chat = db.session.query(chats).filter(chats.c.chat_id == chat_id).first()
    if not chat:
        abort(404, message=f'Chat {chat_id} does not exist')
    return chat


def abort_if_not_a_participant(user_id: int, chat: Row):
    """Makes an abort if user with the given id is not a participant of the given chat"""
    if chat.user1_id != user_id and chat.user2_id != user_id:
        abort(403, message=f'You are not a participant of this chat {chat.chat_id}')


def return_user_or_abort(user_id: int) -> 'User':
    """Returns user model instance if it exists, else - makes abort"""
    try:
        return User.get_user_by_id(user_id)
    except UserNotFoundByIndexError:
        abort(404, message=f'User {user_id} does not exist')
