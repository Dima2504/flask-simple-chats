"""Necessary database tables to provide minimal chats application"""
from app import db
from app.authentication.models import User
import datetime


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
    sender = db.relationship('User', foreign_keys=[sender_id], backref='messages_sent')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='messages_received')



