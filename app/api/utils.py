from sqlalchemy.engine.row import Row
from app.authentication.models import User, chats
from app.authentication.exceptions import UserNotFoundByIndexError
from app.chats.models import Message
from app.chats.exceptions import MessageNotFoundByIndexError
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


def abort_if_not_from_a_chat(chat_id: int, message: Message):
    """Makes an abort if the message  is not from the chat with the given id"""
    if message.chat_id != chat_id:
        abort(404, message=f'Message {message.message_id} is not from the chat {chat_id}')


def abort_if_not_own(user_id: int, message: Message):
    """Makes an abort if the given message was sent not by a user with the given id"""
    if message.sender_id != user_id:
        abort(400, message=f'Message {message.message_id} does not belong to you')


def return_user_or_abort(user_id: int) -> 'User':
    """Returns user model instance if it exists, else - makes abort"""
    try:
        return User.get_user_by_id(user_id)
    except UserNotFoundByIndexError:
        abort(404, message=f'User {user_id} does not exist')


def return_message_or_abort(message_id: int) -> 'Message':
    """Returns message instance by id if it exists, if not - raises abort"""
    try:
        return Message.get_message_by_id(message_id)
    except MessageNotFoundByIndexError:
        abort(404, message=f'Message {message_id} does not exist')
