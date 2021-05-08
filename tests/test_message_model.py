from app import make_app
from app.config import TestConfig
from app import db
from app.authentication import User
from app.authentication.models import chats
from app.chats import Message
import unittest
from datetime import datetime
from sqlalchemy import select


class MessageModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        User.is_chat_between.cache_clear()
        User.get_chat_id_by_users_ids.cache_clear()
        self.app = make_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        User.is_chat_between.cache_clear()
        User.get_chat_id_by_users_ids.cache_clear()

    def test_message_init(self):
        user1 = User(email='user1@gmail.com', username='user1', password_hash='123')
        user2 = User(email='user2@gmail.com', username='user2', password_hash='223')
        db.session.add_all([user1, user2])
        db.session.commit()
        message = Message(text='blabla', datetime_writing=datetime.now(), sender_id=2, receiver_id=1)
        self.assertEqual(message.chat_id, 1)
        db.session.add(message)
        db.session.commit()
        result = db.session.execute(select(chats))
        self.assertEqual(len(result.all()), 1)
        result.close()
        with self.assertRaises(AssertionError):
            Message(text='blabla', datetime_writing=datetime.now(), sender_id=1, receiver_id=2, chat_id=3)

    def test_delete_messages(self):
        user1 = User(email='user1@gmail.com', username='user1', password_hash='123')
        user2 = User(email='user2@gmail.com', username='user2', password_hash='223')
        user3 = User(email='user3@gmail.com', username='user3', password_hash='223')
        m1 = Message(text='blabla', sender_id=2, receiver_id=1)
        m2 = Message(text='blabla2', sender_id=1, receiver_id=2)
        m3 = Message(text='blabla3', sender_id=1, receiver_id=2)

        m4 = Message(text='blabla4', sender_id=1, receiver_id=3)
        m5 = Message(text='blabla5', sender_id=3, receiver_id=1)

        db.session.add_all([user1, user2, user3, m1, m2, m3, m4, m5])
        db.session.commit()
        self.assertEqual(len(Message.query.all()), 5)
        Message.delete_messages(two_users_ids=[2, 1])
        db.session.commit()
        self.assertEqual(len(Message.query.all()), 2)
        Message.delete_messages(chat_id=2)
        db.session.commit()
        self.assertEqual(len(Message.query.all()), 0)






