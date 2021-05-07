import unittest
from app import make_app
from app import db
from app import mail
from app.config import TestConfig
from app.authentication import User
from app.authentication.exceptions import UserNotFoundByIndexError
from app.chats.exceptions import ChatAlreadyExistsError, ChatNotFoundByIndexesError
from app.authentication.models import chats
from sqlalchemy.sql import select
from itsdangerous.exc import SignatureExpired, BadSignature
import os
import time


class UserModelTestCase(unittest.TestCase):
    """Tests for main user model"""
    def setUp(self) -> None:
        self.app = make_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        User.is_chat_between.cache_clear()
        User.get_chat_id_by_users_ids.cache_clear()
        db.create_all()

    def tearDown(self) -> None:
        User.is_chat_between.cache_clear()
        User.get_chat_id_by_users_ids.cache_clear()
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

    def test_send_mail(self):
        user1 = User(email='user1@gmail.com', username='user1', password_hash='123')
        user2 = User(email='user2@gmail.com', username='user2', password_hash='123')
        db.session.add_all([user1, user2])
        db.session.commit()
        with mail.record_messages() as records:
            user1.send_email(subject='Testing_subject1', text='testing_text1')
            user2.send_email(subject='Testing_subject2', text='testing_text2')
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0].subject, 'Testing_subject1')
            self.assertEqual(records[0].body, 'testing_text1')
            self.assertEqual(records[1].subject, 'Testing_subject2')
            self.assertEqual(records[1].body, 'testing_text2')

    def test_reset_password_token(self):
        user1 = User(email='user1@gmail.com', username='user1', password_hash='123')
        user2 = User(email='user2@gmail.com', username='user2', password_hash='123')
        db.session.add_all([user1, user2])
        db.session.commit()
        token1 = user1.get_reset_password_token()
        token2 = user2.get_reset_password_token()
        self.assertEqual(user1, User.get_user_by_reset_password_token(token1))
        self.assertEqual(user2, User.get_user_by_reset_password_token(token2))

    def test_expired_password_token(self):
        user = User(email='user@gmail.com', username='user', password_hash='123')
        db.session.add(user)
        db.session.commit()
        token = user.get_reset_password_token(1)
        time.sleep(2)
        with self.assertRaises(SignatureExpired):
            User.get_user_by_reset_password_token(token)

    def test_bad_signature_password_token(self):
        user = User(email='user@gmail.com', username='user', password_hash='123')
        db.session.add(user)
        db.session.commit()
        token = user.get_reset_password_token()
        token = token[:10]
        with self.assertRaises(BadSignature):
            User.get_user_by_reset_password_token(token)

    def test_users_create_delete_chat(self):
        user1 = User(email='user1@gmail.com', username='user1', password_hash='123')
        user2 = User(email='user2@gmail.com', username='user2', password_hash='123')
        db.session.add_all([user1, user2, ])
        db.session.commit()

        with self.assertRaises(ChatNotFoundByIndexesError):
            User.delete_chat(1, 2)

        self.assertFalse(User.is_chat_between(1, 2))
        self.assertFalse(User.is_chat_between(2, 1))
        result = db.session.execute(select(chats))
        self.assertEqual(len(result.all()), 0)
        result.close()

        User.create_chat(1, 2)
        db.session.commit()
        with self.assertRaises(ChatAlreadyExistsError):
            User.create_chat(2, 1)
        self.assertTrue(User.is_chat_between(1, 2))
        self.assertTrue(User.is_chat_between(2, 1))
        result = db.session.execute(select(chats))
        self.assertEqual(result.all()[0], (1, 1, 2))
        result.close()

        User.delete_chat(1, 2)
        User.create_chat(2, 1)
        db.session.commit()
        self.assertTrue(User.is_chat_between(1, 2))
        self.assertTrue(User.is_chat_between(2, 1))
        result = db.session.execute(select(chats))
        self.assertEqual(result.all()[0], (1, 1, 2))
        result.close()

        User.delete_chat(2, 1)
        db.session.commit()
        self.assertFalse(User.is_chat_between(1, 2))
        self.assertFalse(User.is_chat_between(2, 1))
        result = db.session.execute(select(chats))
        self.assertEqual(len(result.all()), 0)
        result.close()

    def test_get_chat_id_by_users_ids(self):
        user1 = User(email='user1@gmail.com', username='user1', password_hash='123')
        user2 = User(email='user2@gmail.com', username='user2', password_hash='123')
        user3 = User(email='user3@gmail.com', username='user3', password_hash='123')
        db.session.add_all([user1, user2, user3, ])
        db.session.commit()
        with self.assertRaises(ChatNotFoundByIndexesError):
            User.get_chat_id_by_users_ids(1, 2)
        with self.assertRaises(ChatNotFoundByIndexesError):
            User.get_chat_id_by_users_ids(2, 1)
        User.create_chat(1, 2)
        User.create_chat(2, 3)
        db.session.commit()
        self.assertTrue(User.get_chat_id_by_users_ids(1, 2) == User.get_chat_id_by_users_ids(2, 1))
        self.assertTrue(User.get_chat_id_by_users_ids(2, 3) == User.get_chat_id_by_users_ids(3, 2))
        with self.assertRaises(ChatNotFoundByIndexesError):
            User.get_chat_id_by_users_ids(1, 3)
        User.delete_chat(3, 2)
        User.delete_chat(2, 1)
        db.session.commit()
        with self.assertRaises(ChatNotFoundByIndexesError):
            User.get_chat_id_by_users_ids(2, 3)
        with self.assertRaises(ChatNotFoundByIndexesError):
            User.get_chat_id_by_users_ids(1, 2)

    def test_authentication_token(self):
        user = User(email='user1@gmail.com', username='user1', password_hash='123')
        db.session.add(user)
        db.session.commit()
        token = user.get_authentication_token()
        self.assertEqual(user, User.get_user_by_authentication_token(token))

        token_modified = token + 'blabla'
        with self.assertRaises(BadSignature):
            User.get_user_by_authentication_token(token_modified)

        token_expired = user.get_authentication_token(expires_in=1)
        time.sleep(1.5)
        with self.assertRaises(SignatureExpired):
            User.get_user_by_authentication_token(token_expired)













