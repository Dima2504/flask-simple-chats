import unittest
from app import make_app
from app import db
from app.config import TestConfig
from app.authentication import User
from app.authentication.exceptions import UserNotFoundByIndexError
import os


class UserModelTestCase(unittest.TestCase):
    """Tests for main user model"""
    def setUp(self) -> None:
        self.app = make_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_user_by_id(self):
        user1 = User(email='user1@gmail.com', username='user1', password_hash='123')
        user2 = User(email='user2@gmail.com', username='user2', password_hash='223')
        db.session.add_all([user1, user2])
        db.session.commit()
        self.assertEqual(User.get_user_by_id(1), user1)
        self.assertEqual(User.get_user_by_id(2), user2)
        with self.assertRaises(UserNotFoundByIndexError):
            User.get_user_by_id(3)

    def test_set_password(self):
        user = User(email='user@gmail.com', username='user')
        user.set_password('1234')
        self.assertIsNotNone(user.password_hash)

    def test_no_password_attribute(self):
        user = User(email='user@gmail.com', username='user')
        user.set_password('1234')
        with self.assertRaises(AttributeError):
            print(user.password)

    def test_verify_password(self):
        user = User(email='user@gmail.com', username='user')
        for _ in range(5):
            temp_password = os.urandom(10).decode('latin1')
            user.set_password(temp_password)
            self.assertTrue(user.verify_password(temp_password))
            self.assertFalse(user.verify_password('Impossible string???'))

    def test_password_salt(self):
        user1 = User(email='user1@gmail.com', username='user1')
        user2 = User(email='user2@gmail.com', username='user2')
        password = os.urandom(10).decode('latin1')
        user1.set_password(password)
        user2.set_password(password)
        self.assertNotEqual(user1.password_hash, user2.password_hash)



