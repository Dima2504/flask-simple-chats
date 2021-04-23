from app import make_app
from app import db
from app import mail
from app.config import TestConfig
from app.authentication.models import User
from flask import session
from flask import get_flashed_messages
from sqlalchemy.sql import exists
import unittest
import re


class ClientTestCase(unittest.TestCase):
    """Resembles standard interaction with a client"""

    def setUp(self) -> None:
        self.app = make_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_client = self.app.test_client()
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register(self):
        response = self.test_client.post('/authentication/register',
                                         data={'email': 'test@gmail.com', 'username': 'test_user',
                                               'name': 'Ann', 'password1': 'Who am I', 'password2': 'Who am I'},
                                         follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(db.session.query(exists().where(User.email == 'test@gmail.com')))
        user = User.query.filter_by(email='test@gmail.com').first()
        self.assertEqual(user.username, 'test_user')
        self.assertEqual(user.name, 'Ann')
        self.assertTrue(user.verify_password('Who am I'))

    def test_login_logout(self):
        with self.test_client as client:
            client.post('/authentication/register',
                        data={'email': 'test@gmail.com', 'username': 'test_user',
                              'name': 'Ann', 'password1': 'Who am I', 'password2': 'Who am I'},
                        follow_redirects=True)
            self.assertFalse('current_user_id' in session)

            response_login = client.post('/authentication/login', data={'email': 'test@gmail.com',
                                                                        'password': 'Who am I'},
                                         follow_redirects=True)
            self.assertEqual(response_login.status_code, 200)
            self.assertTrue('<title>Simple chats</title>', response_login.data.decode())
            self.assertTrue('current_user_id' in session)

            response_logout = client.get('/authentication/logout', follow_redirects=True)
            self.assertEqual(response_logout.status_code, 200)
            self.assertFalse('current_user_id' in session)

    def test_forgot_reset_password(self):
        self.test_client.post('/authentication/register',
                              data={'email': 'test@gmail.com', 'username': 'test_user',
                                    'name': 'Ann', 'password1': 'I will be forgotten',
                                    'password2': 'I will be forgotten'},
                              follow_redirects=True)
        user = User.query.filter_by(email='test@gmail.com').first()
        self.assertTrue(user.verify_password('I will be forgotten'))

        with mail.record_messages() as records:
            self.test_client.post('/authentication/forgot_password', data={'email': 'test@gmail.com'},
                                  follow_redirects=True)
            self.assertEqual(len(records), 1)
            token_pattern = 'https?://.+/(.+)'
            match = re.search(token_pattern, records[0].body)
            token = match[1]

        response_reset_get = self.test_client.get(f'/authentication/reset_password/{token}')
        self.assertTrue('<title>Reset</title>' in response_reset_get.data.decode())
        self.test_client.post(f'/authentication/reset_password/{token}',
                              data={'password1': 'New password', 'password2': 'New password'})
        self.assertTrue(user.verify_password('New password'))

    def test_anonymous_required(self):
        with self.test_client as client:
            client.post('/authentication/register',
                        data={'email': 'test@gmail.com', 'username': 'test_user',
                              'name': 'Ann', 'password1': 'Who am I', 'password2': 'Who am I'},
                        follow_redirects=True)

            client.post('/authentication/login', data={'email': 'test@gmail.com', 'password': 'Who am I'},
                        follow_redirects=True)

            response = client.get('/authentication/register')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(get_flashed_messages(), ['You have been already logged in', ])

    def test_register_get(self):
        response = self.test_client.get('/authentication/register')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('<title>Register</title>' in response.data.decode())

    def test_login_get(self):
        response = self.test_client.get('/authentication/login')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('<title>Login</title>' in response.data.decode())

    def test_forgot_password_get(self):
        response = self.test_client.get('/authentication/forgot_password')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('<title>Forgot</title>' in response.data.decode())

    def test_reset_password_invalid_token_get(self):
        """This view required only valid token, so, the response is 404"""
        response = self.test_client.get('/authentication/reset_password/invalid_token')
        self.assertEqual(response.status_code, 404)
        self.assertTrue('<title>Page not found</title>' in response.data.decode())
