import functools
from sqlalchemy import or_, desc, case, func
from app.authentication.models import User
from app.chats.models import Message
from app import db
from flask_sqlalchemy import BaseQuery


@functools.lru_cache(maxsize=256)
def get_users_unique_room_name(username1: str, username2: str) -> str:
    """
    Makes unique room name for any two users. Usernames are unique, so, generated room name is unique for every couple
    of users. If usernames are given in different orders, result is the same.
    In order to prevent from frequent recalculations, lru_cache is used.
    Raises value error if usernames are equal.
    :param username1: first user's username
    :type username1: str
    :param username2: second user's username
    :type username2: str
    :return: prepared room's name
    :rtype: str
    """
    if username1 == username2:
        raise ValueError('Given usernames are equal but they cannot be')
    return '_'.join(sorted([username1.strip(), username2.strip()]))


def get_user_chats_and_last_messages(user_id: int) -> BaseQuery:
    """
    Takes a certain user id and makes one pretty complex SQL query. After executing we obtain a list, where each object
    represents one chat user has already started. The object also contains a last message text and datetime_writing,
    companion username and name. The sequence of chats is returned in descending order, from the newest one from the
    oldest.
    The sql query to execute is like:
    # SELECT users.username, users.name, messages.text, messages.datetime_writing FROM messages JOIN (SELECT
    MAX(datetime_writing) AS max_datetime FROM messages WHERE sender_id = [user_id] OR receiver_id = [user_id]
    GROUP BY chat_id) AS max_dates ON messages.datetime_writing = max_dates.max_datetime JOIN users ON users.user_id =
    (CASE WHEN messages.receiver_id = [user_id] THEN messages.sender_id ELSE messages.receiver_id END)
    ORDER BY messages.datetime_writing;
    If there is a way to make it easier, I won't be against to try it out.
    :param user_id: user id for a query
    :type user_id: int
    :return: return a :class:`BaseQuery` instance which has not been executed yet.
    :rtype: BaseQuery
    """
    subquery = db.session.query(func.max(Message.datetime_writing).label('max_datetime')).filter(
        or_(Message.sender_id == user_id, Message.receiver_id == user_id)).group_by(
        Message.chat_id).subquery()

    case_stmt = case((Message.receiver_id == user_id, Message.sender_id), else_=Message.receiver_id)

    result = db.session.query(User.username, User.name, Message.text, Message.datetime_writing).join(
        subquery,
        Message.datetime_writing == subquery.c.max_datetime).join(User, User.user_id == case_stmt).order_by(
        desc(Message.datetime_writing))
    return result
