from app import make_app
from app.config import TestConfig
from app import db
from app.authentication import User
from app.chats.exceptions import ChatNotFoundByIndexesError, ChatAlreadyExistsError
from app.chats import Message
import unittest
from datetime import datetime


class MessageModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = make_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_message_init(self):
        user1 = User(email='user1@gmail.com', username='user1', password_hash='123')
        user2 = User(email='user2@gmail.com', username='user2', password_hash='223')
        db.session.add_all([user1, user2])
        db.session.commit()
        with self.assertRaises(ChatNotFoundByIndexesError):
            Message(text='blabla', datetime_writing=datetime.now(), sender_id=1, receiver_id=2)
        User.create_chat(1, 2)
        message = Message(text='blabla', datetime_writing=datetime.now(), sender_id=2, receiver_id=1)
        self.assertEqual(message.chat_id, 1)
        with self.assertRaises(AssertionError):
            Message(text='blabla', datetime_writing=datetime.now(), sender_id=1, receiver_id=2, chat_id=3)
