import unittest
from typing import List

from werkzeug.exceptions import NotFound, Forbidden

from app import db
from app import make_app
from app.api.utils import abort_if_not_own, abort_if_not_a_participant, abort_if_not_from_a_chat
from app.api.utils import longer_than_zero
from app.api.utils import model_filter_by_get_params as mod_fil
from app.api.utils import return_chat_or_abort, return_user_or_abort, return_message_or_abort
from app.authentication.models import User
from app.chats.models import Message
from app.config import TestConfig
from tests.test_user_model import init_users


class ApiUtilsTestCase(unittest.TestCase):
    """Tests utils from api blueprint"""

    def setUp(self) -> None:
        User.is_chat_between.cache_clear()
        User.get_chat_id_by_users_ids.cache_clear()
        self.app = make_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_client = self.app.test_client()
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        User.is_chat_between.cache_clear()
        User.get_chat_id_by_users_ids.cache_clear()

    def test_return_chat_or_abort(self):
        users = init_users(2)
        User.create_chat(1, 2)
        db.session.add_all(users)
        db.session.commit()
        chat = return_chat_or_abort(1)
        self.assertEqual(chat.user1_id, 1)
        self.assertEqual(chat.user2_id, 2)
        with self.assertRaises(NotFound):
            return_chat_or_abort(2)

    def test_return_user_or_abort(self):
        user1, user2 = init_users(2)
        db.session.add_all([user1, user2])
        self.assertEqual(return_user_or_abort(1), user1)
        self.assertEqual(return_user_or_abort(2), user2)
        with self.assertRaises(NotFound):
            return_user_or_abort(3)

    def test_return_message_or_abort(self):
        users = init_users(2)
        m1 = Message(text='blabla', sender_id=2, receiver_id=1)
        m2 = Message(text='blabla2', sender_id=1, receiver_id=2)
        db.session.add_all(users + [m1, m2])
        db.session.commit()
        self.assertEqual(return_message_or_abort(1), m1)
        self.assertEqual(return_message_or_abort(2), m2)
        with self.assertRaises(NotFound):
            return_message_or_abort(3)

    def test_abort_if_not_own(self):
        users = init_users(2)
        m1 = Message(text='blabla', sender_id=2, receiver_id=1)
        m2 = Message(text='blabla2', sender_id=1, receiver_id=2)
        db.session.add_all(users + [m1, m2])
        db.session.commit()
        with self.assertRaises(Forbidden):
            abort_if_not_own(1, m1)
        try:
            abort_if_not_own(1, m2)
        except Forbidden:
            self.fail(msg="403 error must not have been raised")

    def test_abort_if_not_a_participant(self):
        users = init_users(3)
        User.create_chat(1, 2)
        User.create_chat(2, 3)
        db.session.add_all(users)
        with self.assertRaises(Forbidden):
            abort_if_not_a_participant(1, return_chat_or_abort(2))
        try:
            abort_if_not_a_participant(2, return_chat_or_abort(2))
        except Forbidden:
            self.fail(msg="403 error must not have been raised")

    def test_abort_if_not_from_a_chat(self):
        users = init_users(3)
        m1 = Message(text='blabla', sender_id=2, receiver_id=1)
        m2 = Message(text='blabla2', sender_id=1, receiver_id=3)
        db.session.add_all(users + [m1, m2])
        db.session.commit()
        with self.assertRaises(Forbidden):
            abort_if_not_from_a_chat(2, m1)
        try:
            abort_if_not_from_a_chat(2, m2)
        except Forbidden:
            self.fail(msg="403 error must not have been raised")

    def test_model_filter_by_get_params(self):
        users = init_users(5)

        user_with_an_existing_name = User(email='user6@gmail.com', username='user6', name='name5',
                                          password_hash='123')
        users.append(user_with_an_existing_name)
        db.session.add_all(users)
        db.session.commit()
        users_simple_query = User.query
        self.assertEqual(users_simple_query.all(), users)

        # exact matches:
        self.assertEqual(mod_fil(User, users_simple_query, {'username': 'user2'}).all(), users[1:2])
        self.assertEqual(mod_fil(User, users_simple_query, {'name': 'name4'}).all(), users[3:4])
        self.assertEqual(mod_fil(User, users_simple_query, {'name': 'name5'}).all(), users[4:6])
        self.assertEqual(len(mod_fil(User, users_simple_query, {'name': 'name5', 'username': 'user4'}).all()), 0)
        self.assertEqual(mod_fil(User, users_simple_query, {'user_id': '1'}).all(), users[0:1])

        # '-like' stmt:
        self.assertEqual(len(mod_fil(User, users_simple_query, {'username-like': 'user'}).all()), 6)
        self.assertEqual(len(mod_fil(User, users_simple_query, {'name-like': 'name'}).all()), 6)
        self.assertEqual(mod_fil(User, users_simple_query, {'name-like': '5'}).all(), users[4:6])
        self.assertEqual(mod_fil(User, users_simple_query, {'username-like': 'user1'}).all(), users[0:1])

        # 'ordered-by' and 'ordered-by-desc' stmts:
        self.assertEqual(mod_fil(User, users_simple_query, {'ordered-by': 'date_joined'}).all(), users)
        self.assertEqual(mod_fil(User, users_simple_query, {'ordered-by-desc': 'date_joined'}).all(),
                         list(reversed(users)))
        self.assertEqual(mod_fil(User, users_simple_query, {'ordered-by-desc': 'username'}).all(),
                         list(reversed(users)))

        # 'limit' and 'offset' stmts:
        self.assertEqual(mod_fil(User, users_simple_query, {'limit': 2}).all(), users[:2])
        self.assertEqual(mod_fil(User, users_simple_query, {'offset': 3}).all(), users[3:])
        self.assertEqual(mod_fil(User, users_simple_query, {'offset': 4, 'limit': 1}).all(), users[4:5])
        self.assertEqual(mod_fil(User, users_simple_query, {'offset': 1, 'limit': 2}).all(), users[1:3])

        # some queries combinations:
        self.assertEqual(
            mod_fil(User, users_simple_query, {'ordered-by-desc': 'date_joined', 'offset': 1, 'limit': 2}).all(),
            list(reversed(users))[1:3])
        self.assertEqual(
            mod_fil(User, users_simple_query, {'ordered-by-desc': 'username', 'offset': 4}).all(),
            list(reversed(users))[4:])
        self.assertEqual(
            mod_fil(User, users_simple_query, {'name': 'name5', 'ordered-by-desc': 'username'}).all(),
            list(reversed(users[4:6])))
        self.assertEqual(
            mod_fil(User, users_simple_query, {'name': 'name5', 'ordered-by-desc': 'username', 'limit': 1}).all(),
            list(reversed(users[4:6]))[:1])

        # invalid values:
        self.assertEqual(mod_fil(User, users_simple_query, {'invalid': 'value'}).all(), users)
        self.assertEqual(
            mod_fil(User, users_simple_query, {'invalid': 'value', 'ordered-by-desc': 'date_joined'}).all(),
            list(reversed(users)))

    def test_longer_than_zero(self):
        with self.assertRaises(ValueError):
            longer_than_zero('')
        self.assertEqual(longer_than_zero(432), '432')
        self.assertEqual(longer_than_zero({}), '{}')
