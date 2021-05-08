"""Necessary database tables to provide minimal chats application"""
from app import db
import datetime
from app.authentication.models import User


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
            assert kwargs['chat_id'] == User.get_chat_id_by_users_ids(kwargs['sender_id'],
                                                                      kwargs['receiver_id']), 'Not acceptable at all!!!'
        super().__init__(*args, **kwargs)
