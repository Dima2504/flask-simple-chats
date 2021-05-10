from sqlalchemy.engine.row import Row
from app.authentication.models import User, chats
from app.authentication.exceptions import UserNotFoundByIndexError
from app.chats.models import Message
from app.chats.exceptions import MessageNotFoundByIndexError
from flask_restful import abort
from app import db
from sqlalchemy.sql.sqltypes import String
from sqlalchemy import desc
from flask_sqlalchemy.model import DefaultMeta
from flask_sqlalchemy import BaseQuery


def model_filter_by_get_params(model: DefaultMeta, query: BaseQuery, args: dict) -> BaseQuery:
    """
    Here is implemented a search and filtering the model by request url params. There are several possible variants of
    search, and, of course, they can be easily combined to attain the necessary result.
    Method received three obligatory parameters: model - sqlalchemy orm model class, query - :class:`BaseQuery` object
    to filtering and args - dict of already parsed url params.
        1. User can look for the model instances by putting columns names directly and their theoretical values, like:
            http://localhost:5000/api/users?username=dima&name=dmytro. Such queries will select only exact matches.
        2. To search without an exact match use `-like` ending after db columns names. It works only if column has type
            :class:`sqlalchemy.sql.sqltypes.String` and gives the result from sql `LIKE` statement. Common url looks
            like: http://localhost:5000/api/users?username-like=ma
        3. To sort an output use 'ordered-by' and 'ordered-by-desc' parameter and specify db column name to order by:
            http://localhost:5000/api/users?name-like=a&ordered-by=username
        4. To restrict the number of results user 'limit' and 'offset' statements together or separately:
            http://localhost:5000/api/users?name-like=a&ordered-by=username&limit=2&offset=3

        A simple use case is below::

            from flask import request
            from app import db
            @route('/')
            def index():
                users = User.query
                users = model_filter_by_get_params(User, users, request.args).all()

    If given params are not valid, they will be ignored.
    The function can pe applied for different models and queries and can be expanded if it is necessary.
    :param model: model base class
    :type model: DefaultMeta
    :param query: not executed query object to filtering
    :type query: BaseQuery
    :param args: url query parameters
    :type args: dict
    :return: not executed filtered query object
    :rtype: BaseQuery
    """
    model_columns = model.__table__.c.keys()
    for k, v in args.items():
        if k == 'ordered-by':
            if v in model_columns:
                query = query.order_by(getattr(model, v))
        elif k == 'ordered-by-desc':
            if v in model_columns:
                query = query.order_by(desc(getattr(model, v)))
        elif k.endswith('-like'):
            attr = k.split('-like')[0]
            if attr in model_columns and isinstance(model.__table__.c.get(attr).type, String):
                query = query.filter(getattr(model, attr).ilike(f'%{v}%'))
        elif k in model_columns:
            query = query.filter(getattr(model, k) == v)
    if 'limit' in args:
        query = query.limit(int(args.get('limit')))
    if 'offset' in args:
        query = query.offset(int(args.get('offset')))
    return query


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
