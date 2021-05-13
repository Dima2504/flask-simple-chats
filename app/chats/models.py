"""Necessary database tables to provide minimal chats application"""
import datetime

from sqlalchemy import delete

from app import db
from app.authentication.models import User
from .exceptions import MessageNotFoundByIndexError


class Message(db.Model):
    """Each tuple in database contains information about one sms: id, data time of writing, sender's id, receiver's id
    and text of the message
    """
    __tablename__ = 'messages'
    message_id = db.Column(db.Integer, primary_key=True)
    datetime_writing = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    text = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.chat_id'), nullable=False)
    sender = db.relationship('User', foreign_keys=[sender_id], backref='messages_sent')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='messages_received')

    def __init__(self, *args, **kwargs):
        sender_id = kwargs.get('sender_id')
        receiver_id = kwargs.get('receiver_id')
        if not User.is_chat_between(sender_id, receiver_id):
            User.create_chat(sender_id, receiver_id)
        if 'chat_id' not in kwargs:
            self.chat_id = User.get_chat_id_by_users_ids(sender_id, receiver_id)
        else:
            assert kwargs['chat_id'] == User.get_chat_id_by_users_ids(sender_id,
                                                                      receiver_id), 'Not acceptable at all!!!'
        super().__init__(*args, **kwargs)

    @staticmethod
    def delete_messages(two_users_ids: list = None, chat_id: int = None):
        """
        Deletes all the messages from the chat between two given users in the list. Instead of list, chat id can be
        used directly to delete all the messages from it. Changes must be committed after executing this method in order
        to save them.
        :param two_users_ids: users ids in a list. The chat between them will be deleted
        :type two_users_ids: list
        :param chat_id: the chat, which will be deleted
        :type chat_id: int
        """
        chat_id = chat_id or User.get_chat_id_by_users_ids(*two_users_ids)
        db.session.execute(delete(Message).where(Message.chat_id == chat_id))

    @classmethod
    def get_message_by_id(cls, message_id: int) -> 'Message':
        """Return a certain message instance with given id if exists, else - raise error"""
        message = cls.query.get(message_id)
        if not message:
            raise MessageNotFoundByIndexError
        return message
