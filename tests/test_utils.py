import os
import unittest

from app import db
from app import make_app
from app.authentication.models import User
from app.chats.models import Message
from app.chats.utils import get_user_chats_and_last_messages as get_uc
from app.chats.utils import get_users_unique_room_name as get_rn
from app.chats.utils import search_for_users_by
from app.config import TestConfig
from tests.test_user_model import init_users


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
        users = init_users(5)
        User.create_chat(1, 2)
        User.create_chat(1, 3)
        User.create_chat(1, 4)
        User.create_chat(2, 3)
        db.session.add_all(users)
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

    def test_search_for_users_by(self):
        users = init_users(4)
        users[0].username, users[0].name = 'pasha', 'Pavlo Vasyliovych'
        users[1].username, users[1].name = 'dima', 'Dmitry Andreevich'
        users[2].username, users[2].name = 'maks', 'Maxim Ruslanovich'
        users[3].username, users[3].name = 'ann', 'Anna Alekseevna'
        db.session.add_all(users)
        db.session.commit()
        self.assertEqual(len(search_for_users_by('').all()), 4)
        self.assertEqual(len(search_for_users_by('a').all()), 4)
        result1 = search_for_users_by('a', 2).all()
        self.assertEqual(len(result1), 3)
        for r in result1:
            self.assertNotEqual('dima', r[1])

        self.assertEqual(len(search_for_users_by('dima').all()), 1)
        self.assertEqual(len(search_for_users_by('dima', 1).all()), 1)
        self.assertEqual(len(search_for_users_by('dima', 2).all()), 0)
        self.assertEqual(len(search_for_users_by('ann', 4).all()), 0)

        result2 = search_for_users_by('dima Pavlo').all()
        self.assertEqual(len(result2), 2)
        self.assertEqual(result2[0][0], 'Dmitry Andreevich')
        self.assertEqual(result2[1][0], 'Pavlo Vasyliovych')

        result3 = search_for_users_by('ich').all()
        self.assertEqual(len(result3), 2)
        self.assertEqual(result3[0][0], 'Maxim Ruslanovich')
        self.assertEqual(result3[1][0], 'Dmitry Andreevich')
