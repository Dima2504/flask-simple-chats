import unittest
from app import make_app
from app import db
from app.config import TestConfig
from app.chats.utils import get_users_unique_room_name as get_rn
from app.chats.utils import get_user_chats_and_last_messages as get_uc
from app.authentication.models import User
from app.chats.models import Message
import os


class UtilsTestCase(unittest.TestCase):
    """Tries out additional utils"""
    def setUp(self) -> None:
        get_rn.cache_clear()
        self.app = make_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self) -> None:
        get_rn.cache_clear()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_users_unique_room_name(self):
        usernames = [os.urandom(8).decode('latin1') for _ in range(3)]
        self.assertEqual(get_rn(usernames[0], usernames[1]), get_rn(usernames[1], usernames[0]))
        self.assertEqual(get_rn(usernames[1], usernames[2]), get_rn(usernames[2], usernames[1]))
        self.assertEqual(get_rn(usernames[0], usernames[2]), get_rn(usernames[2], usernames[0]))

        self.assertNotEqual(get_rn(usernames[0], usernames[1]), get_rn(usernames[1], usernames[2]))
        self.assertNotEqual(get_rn(usernames[1], usernames[2]), get_rn(usernames[0], usernames[2]))
        self.assertNotEqual(get_rn(usernames[0], usernames[1]), get_rn(usernames[0], usernames[2]))

        with self.assertRaises(ValueError):
            for i in range(3):
                get_rn(usernames[i], usernames[i])

    def test_get_user_chats_and_last_messages(self):
        user1 = User(email='user1@gmail.com', username='user1', password_hash='123')
        user2 = User(email='user2@gmail.com', username='user2', password_hash='123')
        user3 = User(email='user3@gmail.com', username='user3', password_hash='123')
        user4 = User(email='user4@gmail.com', username='user4', password_hash='123')
        user5 = User(email='user5@gmail.com', username='user5', password_hash='123')
        User.create_chat(1, 2)
        User.create_chat(1, 3)
        User.create_chat(1, 4)
        User.create_chat(2, 3)
        db.session.add_all([user1, user2, user3, user4, user5])
        m1 = Message(text='m1', sender_id=1, receiver_id=2)
        m2 = Message(text='m2', sender_id=2, receiver_id=1)
        m3 = Message(text='m3', sender_id=1, receiver_id=2)

        m4 = Message(text='m4', sender_id=1, receiver_id=3)
        m5 = Message(text='m5', sender_id=3, receiver_id=1)

        m6 = Message(text='m6', sender_id=1, receiver_id=4)

        m7 = Message(text='m7', sender_id=2, receiver_id=3)
        m8 = Message(text='m8', sender_id=3, receiver_id=2)

        db.session.add_all([m1, m2, m3, m4, m5, m6, m7, m8])
        db.session.commit()

        chats1 = get_uc(1).all()
        self.assertEqual(len(chats1), 3)
        self.assertEqual(chats1[0][0], 'user4')
        self.assertEqual(chats1[1][0], 'user3')
        self.assertEqual(chats1[2][0], 'user2')
        self.assertEqual(chats1[0][2], 'm6')
        self.assertEqual(chats1[1][2], 'm5')
        self.assertEqual(chats1[2][2], 'm3')

        chats2 = get_uc(2).all()
        self.assertEqual(len(chats2), 2)
        self.assertEqual(chats2[0][0], 'user3')
        self.assertEqual(chats2[1][0], 'user1')
        self.assertEqual(chats2[0][2], 'm8')
        self.assertEqual(chats2[1][2], 'm3')

        chats3 = get_uc(3).all()
        self.assertEqual(len(chats3), 2)
        self.assertEqual(chats3[0][0], 'user2')
        self.assertEqual(chats3[1][0], 'user1')
        self.assertEqual(chats3[0][2], 'm8')
        self.assertEqual(chats3[1][2], 'm5')

        chats4 = get_uc(4).all()
        self.assertEqual(len(chats4), 1)
        self.assertEqual(chats4[0][0], 'user1')
        self.assertEqual(chats4[0][2], 'm6')

        chats5 = get_uc(5).all()
        self.assertEqual(len(chats5), 0)

