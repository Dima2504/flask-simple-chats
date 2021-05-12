import unittest
from flask import current_app
from app import mail
from app.authentication.models import User, chats
from app.chats.models import Message
from app import make_app
from app import db
from app.config import TestConfig
import base64
import re


class ApiClientTestCase(unittest.TestCase):
    """Tries out rest api functionality"""

    def register_users(self, number: int):
        for i in range(1, number + 1):
            self.test_client.post('/api/register', json={'email': f'user{i}@gmail.com', 'username': f'username{i}',
                                                         'name': f'name{i}', 'password': '12345678'})

    def init_main_user(self, name='main'):
        self.test_client.post('/api/register', json={'email': f'{name}@gmail.com', 'username': f'{name}_username',
                                                     'name': f'{name}_name', 'password': '12345678'})
        self.basic_auth_header = {
            'Authorization': f'Basic {base64.b64encode(f"{name}@gmail.com:12345678".encode()).decode()}'}
        token = self.test_client.get('/api/token', headers=self.basic_auth_header).json['token']
        self.bearer_auth_header = {'Authorization': f'Bearer {token}'}

    def setUp(self) -> None:
        User.is_chat_between.cache_clear()
        User.get_chat_id_by_users_ids.cache_clear()
        self.app = make_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_client = self.app.test_client()
        db.create_all()

    def tearDown(self) -> None:
        User.is_chat_between.cache_clear()
        User.get_chat_id_by_users_ids.cache_clear()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register(self):
        self.assertEqual(len(User.query.all()), 0)
        response = self.test_client.post('/api/register', json={'email': 'test@gmail.com', 'username': 'test_username',
                                                                'name': 'test_name', 'password': '12345678'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(User.query.all()), 1)
        user = User.get_user_by_id(1)
        self.assertTrue(
            user.email == 'test@gmail.com' and user.username == 'test_username' and user.name == 'test_name' and
            user.verify_password('12345678'))
        # an existing email
        response = self.test_client.post('/api/register', json={'email': 'test@gmail.com', 'username': 'test',
                                                                'name': 'test_name', 'password': '12345678'})
        self.assertEqual(response.status_code, 400)
        # an existing username
        response = self.test_client.post('/api/register', json={'email': 'test2@gmail.com', 'username': 'test_username',
                                                                'name': 'test_name', 'password': '12345678'})
        self.assertEqual(response.status_code, 400)
        # an invalid email
        response = self.test_client.post('/api/register', json={'email': 'test-gmail.com', 'username': 'test_username',
                                                                'name': 'test_name', 'password': '12345678'})
        self.assertEqual(response.status_code, 400)
        # an invalid username
        response = self.test_client.post('/api/register', json={'email': 'test2@gmail.com', 'username': 'te',
                                                                'name': 'test_name', 'password': '12345678'})
        self.assertEqual(response.status_code, 400)
        # an invalid name
        response = self.test_client.post('/api/register', json={'email': 'test2@gmail.com', 'username': 'test',
                                                                'name': 'te', 'password': '12345678'})
        self.assertEqual(response.status_code, 400)
        # an invalid password
        response = self.test_client.post('/api/register', json={'email': 'test2@gmail.com', 'username': 'test',
                                                                'name': 'test', 'password': 'gfd'})
        self.assertEqual(response.status_code, 400)

    def test_token(self):
        self.test_client.post('/api/register', json={'email': 'test@gmail.com', 'username': 'test_username',
                                                     'name': 'test_name', 'password': '12345678'})
        response = self.test_client.get('/api/token', headers={
            'Authorization': f'Basic {base64.b64encode(b"test@gmail.com:12345678").decode()}'})
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['expires_in'], current_app.config['AUTHENTICATION_TOKEN_DEFAULT_EXPIRES_IN'])
        self.assertEqual(User.get_user_by_authentication_token(data['token']).email, 'test@gmail.com')
        response = self.test_client.get('/api/token', headers={'Authorization': f'Bearer {data["token"]}'})
        self.assertEqual(response.status_code, 200)

    def test_forgot_reset_password(self):
        self.init_main_user()
        user = User.get_user_by_id(1)
        self.assertTrue(user.verify_password('12345678'))
        with mail.record_messages() as records:
            response = self.test_client.post('/api/forgot-password', json={'email': user.email})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(records), 1)
            token_pattern = '"(.+)"'
            match = re.search(token_pattern, records[0].body)
            token = match[1]

        response = self.test_client.post('/api/reset-password', json={'token': token, 'password': '87654321'})
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json['email'], user.email)
        self.assertTrue(user.verify_password('87654321'))

    def test_update(self):
        self.init_main_user()
        user = User.get_user_by_id(1)
        self.assertEqual(user.username, 'main_username')
        self.assertEqual(user.name, 'main_name')
        response = self.test_client.post('/api/update', json={'name': 'new_name'}, headers=self.basic_auth_header)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(user.name, 'new_name')
        self.assertEqual(response.json['name'], 'new_name')
        response = self.test_client.post('/api/update', json={'username': 'new_username'},
                                         headers=self.bearer_auth_header)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(user.username, 'new_username')
        self.assertEqual(response.json['username'], 'new_username')
        response = self.test_client.post('/api/update', json={'name': 'old_name', 'username': 'old_username'},
                                         headers=self.bearer_auth_header)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(user.name, 'old_name')
        self.assertEqual(user.username, 'old_username')
        self.assertEqual(response.json['name'], 'old_name')
        self.assertEqual(response.json['username'], 'old_username')

        response = self.test_client.post('/api/update', json={'name': 'old_name'}, headers=self.basic_auth_header)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Nothing was updated')

        response = self.test_client.post('/api/update', json={'username': 'old_username'},
                                         headers=self.bearer_auth_header)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Nothing was updated')

    def test_users_list(self):
        self.register_users(5)
        self.init_main_user()
        response = self.test_client.get('/api/users', headers=self.basic_auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['user_id'], 6)
        self.assertEqual(len(data['data']), 6)
        # except the main user
        for i, user in enumerate(data['data'][:-1]):
            self.assertEqual(user['user_id'], i + 1)
            self.assertEqual(user['username'], f'username{i + 1}')
            self.assertEqual(user['name'], f'name{i + 1}')
            self.assertFalse(user.get('date_joined') is None)

    def test_user_single(self):
        self.register_users(2)
        self.init_main_user()
        response = self.test_client.get('/api/users/1', headers=self.basic_auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['user_id'], 3)
        user = response.json['data']
        self.assertEqual(user['user_id'], 1)
        self.assertEqual(user['username'], 'username1')
        self.assertEqual(user['name'], 'name1')

        response = self.test_client.get('/api/users/2', headers=self.basic_auth_header)
        self.assertEqual(response.status_code, 200)
        user = response.json['data']
        self.assertEqual(user['user_id'], 2)
        self.assertEqual(user['username'], 'username2')
        self.assertEqual(user['name'], 'name2')

        response = self.test_client.get('/api/users/4', headers=self.basic_auth_header)
        self.assertEqual(response.status_code, 404)

    def test_chats_list(self):
        self.init_main_user()
        self.register_users(3)
        User.create_chat(1, 2)
        User.create_chat(1, 3)
        db.session.commit()
        self.assertEqual(db.session.query(chats).count(), 2)
        response = self.test_client.get('/api/chats', headers=self.bearer_auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['user_id'], 1)
        self.assertEqual(len(data['data']), 2)
        chat1, chat2 = data['data']
        self.assertTrue(chat1['chat_id'] == 1 and chat1['user1_id'] == 1 and chat1['user2_id'] == 2)
        self.assertTrue(chat2['chat_id'] == 2 and chat2['user1_id'] == 1 and chat2['user2_id'] == 3)

        response = self.test_client.post('/api/chats', json={'companion_id': 4}, headers=self.bearer_auth_header)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(db.session.query(chats).count(), 3)
        data = response.json
        self.assertTrue(data['user_id'] == 1 and data['companion_id'] == 4 and data['chat_id'] == 3)

        response = self.test_client.get('/api/chats', headers=self.bearer_auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data['data']), 3)
        chat3 = data['data'][2]
        self.assertTrue(chat3['chat_id'] == 3 and chat3['user1_id'] == 1 and chat3['user2_id'] == 4)

        response = self.test_client.post('/api/chats', json={'companion_id': 4}, headers=self.bearer_auth_header)
        self.assertEqual(response.status_code, 400)

    def test_chat_single(self):
        self.init_main_user()
        self.register_users(1)
        self.assertEqual(db.session.query(chats).count(), 0)
        self.assertEqual(db.session.query(Message).count(), 0)
        m1 = Message(text='bla', sender_id=1, receiver_id=2)
        m2 = Message(text='blabla', sender_id=2, receiver_id=1)
        db.session.add_all([m1, m2])
        db.session.commit()
        self.assertEqual(db.session.query(chats).count(), 1)
        self.assertEqual(db.session.query(Message).count(), 2)

        response = self.test_client.get('/api/chats/1', headers=self.bearer_auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['user_id'], 1)
        chat = data['data']
        self.assertTrue(chat['chat_id'] == 1 and chat['user1_id'] == 1 and chat['user2_id'] == 2)

        response = self.test_client.delete('/api/chats/1', headers=self.bearer_auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue(data['user_id'] == 1 and data['chat_id'] == 1)
        self.assertEqual(db.session.query(chats).count(), 0)
        self.assertEqual(db.session.query(Message).count(), 0)

    def test_chat_messages_list_get(self):
        self.init_main_user()
        self.register_users(2)
        m1 = Message(text='bla1', sender_id=1, receiver_id=2)
        m2 = Message(text='bla2', sender_id=2, receiver_id=1)
        m3 = Message(text='bla3', sender_id=1, receiver_id=2)
        m4 = Message(text='bla4', sender_id=2, receiver_id=1)

        m5 = Message(text='bla5', sender_id=1, receiver_id=3)
        m6 = Message(text='bla6', sender_id=3, receiver_id=1)
        db.session.add_all([m1, m2, m3, m4, m5, m6])
        db.session.commit()

        response = self.test_client.get('/api/chats/1/messages', headers=self.bearer_auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue(data['user_id'] == 1 and data['chat_id'] == 1)
        messages = data['data']
        self.assertEqual(len(messages), 4)
        self.assertTrue(
            messages[0]['text'] == 'bla1' and messages[1]['text'] == 'bla2' and messages[2]['text'] == 'bla3' and
            messages[3]['text'] == 'bla4')

        response = self.test_client.get('/api/chats/2/messages', headers=self.bearer_auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue(data['user_id'] == 1 and data['chat_id'] == 2)
        messages = data['data']
        self.assertEqual(len(messages), 2)
        self.assertTrue(messages[0]['text'] == 'bla5' and messages[1]['text'] == 'bla6')

    def test_chat_messages_list_post(self):
        self.init_main_user()
        self.register_users(1)
        User.create_chat(1, 2)
        db.session.commit()
        self.assertEqual(db.session.query(Message).count(), 0)
        response = self.test_client.post('/api/chats/1/messages', json={'texts': ['first']},
                                         headers=self.basic_auth_header)
        self.assertEqual(response.status_code, 201)
        data = response.json
        self.assertTrue(data['user_id'] == 1 and data['chat_id'] == 1)
        self.assertEqual(db.session.query(Message).count(), 1)
        message = Message.query.first()
        self.assertTrue(
            message.text == 'first' and message.sender_id == 1 and message.receiver_id == 2 and message.chat_id == 1)

        response = self.test_client.post('/api/chats/1/messages', json={'texts': ['second', 'third', 'fourth']},
                                         headers=self.bearer_auth_header)
        self.assertEqual(response.status_code, 201)
        data = response.json
        self.assertTrue(data['user_id'] == 1 and data['chat_id'] == 1)
        self.assertEqual(db.session.query(Message).count(), 4)
        new_messages = Message.query.all()[1:]
        self.assertTrue(
            new_messages[0].text == 'second' and new_messages[1].text == 'third' and new_messages[2].text == 'fourth')

    def test_chat_message_single(self):
        self.init_main_user()
        self.register_users(1)
        m1 = Message(text='bla1', sender_id=1, receiver_id=2)
        m2 = Message(text='bla2', sender_id=2, receiver_id=1)
        m3 = Message(text='bla2', sender_id=1, receiver_id=2)
        db.session.add_all([m1, m2, m3])
        db.session.commit()
        response = self.test_client.get('/api/chats/1/messages/2', headers=self.bearer_auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue(data['user_id'] == 1 and data['chat_id'] == 1)
        message = data['data']
        self.assertTrue(message['text'] == 'bla2' and message['sender_id'] == 2 and message['receiver_id'] == 1)

        response = self.test_client.get('/api/chats/1/messages/1', headers=self.bearer_auth_header)
        self.assertEqual(response.status_code, 200)
        data = response.json
        message = data['data']
        self.assertTrue(message['text'] == 'bla1' and message['sender_id'] == 1 and message['receiver_id'] == 2)

        self.assertEqual(db.session.query(Message).count(), 3)
        response = self.test_client.delete('/api/chats/1/messages/3', headers=self.bearer_auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message_id'], 3)

        self.assertEqual(db.session.query(Message).count(), 2)
        response = self.test_client.put('/api/chats/1/messages/1', headers=self.bearer_auth_header,
                                        json={'text': 'new text'})
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue(
            data['user_id'] == 1 and data['chat_id'] == 1 and data['message_id'] == 1 and data['text'] == 'new text')
        self.assertEqual(db.session.query(Message).count(), 2)
        message = Message.query.first()
        self.assertTrue(message.text == 'new text' and message.sender_id == 1 and message.receiver_id == 2)
