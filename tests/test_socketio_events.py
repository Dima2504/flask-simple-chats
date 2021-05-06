from app import make_app
from app import socket_io
from app import db
from app.config import TestConfig
from app.chats import Message
from app.authentication.models import chats, User
import unittest
import time
import random
from datetime import datetime
from flask.testing import FlaskClient
from flask_socketio import SocketIOTestClient
from typing import Tuple
from sqlalchemy import select


class SocketIOEventsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.events_namespace = '/chats/going'
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

    @staticmethod
    def init_two_clients(client1: FlaskClient, client2: FlaskClient):
        """Initializes two given clients for the next actions with socketio events: fills in their sessions with
        necessary information.
        :param client1: the first flask test client instance
        :param client2: the second one"""
        client1.post('/authentication/register',
                     data={'email': 'test1@gmail.com', 'username': 'test_user1',
                           'name': 'Ann1', 'password1': 'Who am I', 'password2': 'Who am I'},
                     follow_redirects=True)
        client1.post('/authentication/login', data={'email': 'test1@gmail.com',
                                                    'password': 'Who am I'},
                     follow_redirects=True)
        client2.post('/authentication/register',
                     data={'email': 'test2@gmail.com', 'username': 'test_user2',
                           'name': 'Ann2', 'password1': 'Who am I', 'password2': 'Who am I'},
                     follow_redirects=True)
        client2.post('/authentication/login', data={'email': 'test2@gmail.com',
                                                    'password': 'Who am I'})
        client1.get('/chats/begin/test_user2')
        client2.get('/chats/begin/test_user1')

    def get_socket_io_clients(self, *clients: FlaskClient) -> Tuple[SocketIOTestClient, ...]:
        """
        For each given flask client instance return socketio test client instance. The function is created only to make
        tests clearer.
        :param clients: sequence of flask test clients instances
        :type clients: FlaskClient
        :return: tuple of initialized socket io test clients.
        :rtype: tuple[SocketIOTestClient]
        """
        return tuple(
            [socket_io.test_client(self.app, namespace=self.events_namespace, flask_test_client=client) for client in
             clients])

    def test_connect_disconnect(self):
        socket_io_client = socket_io.test_client(self.app, namespace=self.events_namespace)
        self.assertTrue(socket_io_client.is_connected(self.events_namespace))
        received = socket_io_client.get_received(self.events_namespace)
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['name'], 'status')
        self.assertEqual(received[0]['args'], [{'message': 'connected'}])
        self.assertEqual(received[0]['namespace'], self.events_namespace)

        socket_io_client.disconnect(self.events_namespace)
        self.assertFalse(socket_io_client.is_connected(self.events_namespace))

    def test_enter_leave_room(self):
        with self.app.test_client() as client1, self.app.test_client() as client2:
            self.init_two_clients(client1, client2)
            socket_io_client1, socket_io_client2 = self.get_socket_io_clients(client1, client2)

            socket_io_client1.emit('enter_room', namespace=self.events_namespace)
            socket_io_client2.emit('enter_room', namespace=self.events_namespace)

            received1 = socket_io_client1.get_received(self.events_namespace)
            received2 = socket_io_client2.get_received(self.events_namespace)

            self.assertEqual(len(received1), 3)
            self.assertEqual(received1[0]['name'], 'status')
            self.assertEqual(received1[0]['args'], [{'message': 'connected'}])
            self.assertEqual(received1[0]['namespace'], self.events_namespace)
            self.assertEqual(received1[1]['name'], 'status')
            self.assertEqual(received1[1]['args'], [{'message': 'Ann1 entered the room'}])
            self.assertEqual(received1[1]['namespace'], self.events_namespace)
            self.assertEqual(received1[2]['name'], 'status')
            self.assertEqual(received1[2]['args'], [{'message': 'Ann2 entered the room'}])
            self.assertEqual(received1[2]['namespace'], self.events_namespace)

            self.assertEqual(len(received2), 2)
            self.assertEqual(received2[0]['name'], 'status')
            self.assertEqual(received2[0]['args'], [{'message': 'connected'}])
            self.assertEqual(received2[0]['namespace'], self.events_namespace)
            self.assertEqual(received2[1]['name'], 'status')
            self.assertEqual(received2[1]['args'], [{'message': 'Ann2 entered the room'}])
            self.assertEqual(received2[1]['namespace'], self.events_namespace)

            socket_io_client1.emit('leave_room', namespace=self.events_namespace)
            received2 = socket_io_client2.get_received(self.events_namespace)
            self.assertEqual(len(received2), 1)
            self.assertEqual(received2[0]['name'], 'status')
            self.assertEqual(received2[0]['args'], [{'message': 'Ann1 left the room'}])
            self.assertEqual(received2[0]['namespace'], self.events_namespace)

    def test_send_messages(self):
        self.assertEqual(len(Message.query.all()), 0)
        with self.app.test_client() as client1, self.app.test_client() as client2:
            self.init_two_clients(client1, client2)
            socket_io_client1, socket_io_client2 = self.get_socket_io_clients(client1, client2)

            socket_io_client1.emit('enter_room', namespace=self.events_namespace)
            socket_io_client2.emit('enter_room', namespace=self.events_namespace)

            # erase status messages
            socket_io_client1.get_received(namespace=self.events_namespace)
            socket_io_client2.get_received(namespace=self.events_namespace)

            first_message_time = time.time()
            second_message_time = time.time()
            socket_io_client1.emit('put_data',
                                   {'message': 'Hello!', 'timestamp_milliseconds': first_message_time * 1000},
                                   namespace=self.events_namespace)
            socket_io_client2.emit('put_data', {'message': 'Hi!', 'timestamp_milliseconds': second_message_time * 1000},
                                   namespace=self.events_namespace)

            received1 = socket_io_client1.get_received(self.events_namespace)
            received2 = socket_io_client2.get_received(self.events_namespace)

            self.assertEqual(len(received1), 2)
            self.assertEqual(len(received2), 2)
            self.assertEqual(received1[0], received2[0])
            self.assertEqual(received1[1], received2[1])

            self.assertTrue(received1[0]['name'] == received1[1]['name'] == 'print_message')
            self.assertEqual(received1[0]['args'][0]['message'], 'Hello!')
            self.assertEqual(received1[1]['args'][0]['message'], 'Hi!')

            messages = Message.query.all()
            self.assertEqual(len(messages), 2)
            self.assertEqual(messages[0].text, 'Hello!')
            self.assertEqual(messages[0].datetime_writing, datetime.utcfromtimestamp(first_message_time))
            self.assertEqual(messages[0].sender_id, 1)
            self.assertEqual(messages[0].receiver_id, 2)

            self.assertEqual(messages[1].text, 'Hi!')
            self.assertEqual(messages[1].datetime_writing, datetime.utcfromtimestamp(second_message_time))
            self.assertEqual(messages[1].sender_id, 2)
            self.assertEqual(messages[1].receiver_id, 1)

    def test_create_chat_in_put_data_event(self):
        with self.app.test_client() as client1, self.app.test_client() as client2:
            self.init_two_clients(client1, client2)
            socket_io_client1, socket_io_client2 = self.get_socket_io_clients(client1, client2)

            socket_io_client1.emit('enter_room', namespace=self.events_namespace)
            socket_io_client2.emit('enter_room', namespace=self.events_namespace)

            result = db.session.execute(select(chats))
            self.assertEqual(len(result.all()), 0)
            result.close()
            self.assertFalse(User.is_chat_between(1, 2))
            self.assertEqual(User.is_chat_between.cache_info().currsize, 1)

            socket_io_client1.emit('put_data',
                                   {'message': 'test_message', 'timestamp_milliseconds': time.time() * 1000},
                                   namespace=self.events_namespace)
            self.assertEqual(User.is_chat_between.cache_info().currsize, 0)
            result = db.session.execute(select(chats))
            self.assertEqual(len(result.all()), 1)
            result.close()
            self.assertTrue(User.is_chat_between(1, 2))
            self.assertTrue(User.is_chat_between(2, 1))
            self.assertEqual(User.is_chat_between.cache_info().currsize, 2)
            User.is_chat_between.cache_clear()
            self.assertTrue(User.is_chat_between(1, 2))
            socket_io_client2.emit('put_data',
                                   {'message': 'test_message2', 'timestamp_milliseconds': time.time() * 1000},
                                   namespace=self.events_namespace)
            self.assertEqual(User.is_chat_between.cache_info().currsize, 2)
            result = db.session.execute(select(chats))
            self.assertEqual(len(result.all()), 1)
            result.close()
            self.assertTrue(User.is_chat_between(2, 1))
            self.assertEqual(User.is_chat_between.cache_info().currsize, 2)

    def test_get_more_messages(self):
        messages_limit = self.app.config['MESSAGES_PER_LOAD_EVENT']
        with self.app.test_client() as client1, self.app.test_client() as client2:
            self.init_two_clients(client1, client2)
            socket_io_client1, socket_io_client2 = self.get_socket_io_clients(client1, client2)
            socket_io_client1.emit('enter_room', namespace=self.events_namespace)
            socket_io_client2.emit('enter_room', namespace=self.events_namespace)
            User.create_chat(1, 2)

            # erase status messages
            socket_io_client1.get_received(namespace=self.events_namespace)
            socket_io_client2.get_received(namespace=self.events_namespace)

            number_of_messages = random.randint(0, 15)
            db.session.add_all(
                [Message(text=str(figure), sender_id=1, receiver_id=2) for figure in range(number_of_messages)])
            db.session.commit()
            self.assertEqual(len(Message.query.all()), number_of_messages)

            for messages_offset in range(0, number_of_messages):
                socket_io_client1.emit('get_more_messages', {'messages_offset': messages_offset},
                                       namespace=self.events_namespace)

                received1 = socket_io_client1.get_received(self.events_namespace)
                received2 = socket_io_client2.get_received(self.events_namespace)

                self.assertEqual(len(received2), 0)
                self.assertEqual(len(received1), 1)
                received_data = received1[0]['args'][0]
                self.assertTrue(received_data['messages_number'] <= messages_limit)
                self.assertEqual(received_data['messages_number'],
                                 number_of_messages - messages_offset if number_of_messages - messages_offset <= messages_limit else messages_limit)

            messages_offset = random.randint(0, number_of_messages)
            socket_io_client1.emit('get_more_messages', {'messages_offset': messages_offset},
                                   namespace=self.events_namespace)
            received1 = socket_io_client1.get_received(self.events_namespace)
            received_messages = received1[0]['args'][0]['messages']
            for message, message_text in zip(received_messages, reversed(range(
                    number_of_messages - messages_offset if number_of_messages - messages_offset <= messages_limit else messages_limit))):
                self.assertTrue(message['is_current_user'])
                self.assertEqual(message['message_text'], str(message_text))

            messages_offset = random.randint(0, number_of_messages)
            socket_io_client2.emit('get_more_messages', {'messages_offset': messages_offset},
                                   namespace=self.events_namespace)
            received2 = socket_io_client2.get_received(self.events_namespace)
            received_messages = received2[0]['args'][0]['messages']
            for message in received_messages:
                self.assertFalse(message['is_current_user'])

    def test_isolated_clients_chat(self):
        with self.app.test_client() as client1, self.app.test_client() as client2, self.app.test_client() as client3:
            self.init_two_clients(client1, client2)

            client3.post('/authentication/register',
                         data={'email': 'test3@gmail.com', 'username': 'test_user3',
                               'name': 'Ann3', 'password1': 'Who am I', 'password2': 'Who am I'},
                         follow_redirects=True)
            client3.post('/authentication/login', data={'email': 'test3@gmail.com',
                                                        'password': 'Who am I'},
                         follow_redirects=True)
            client3.get('/chats/begin/test_user2')

            socket_io_client1, socket_io_client2, socket_io_client3 = self.get_socket_io_clients(client1, client2,
                                                                                                 client3)
            socket_io_client1.emit('enter_room', namespace=self.events_namespace)
            socket_io_client2.emit('enter_room', namespace=self.events_namespace)
            socket_io_client3.emit('enter_room', namespace=self.events_namespace)

            # erase status messages
            socket_io_client1.get_received(namespace=self.events_namespace)
            socket_io_client2.get_received(namespace=self.events_namespace)
            socket_io_client3.get_received(namespace=self.events_namespace)

            socket_io_client1.emit('put_data',
                                   {'message': 'test_message', 'timestamp_milliseconds': time.time() * 1000},
                                   namespace=self.events_namespace)
            self.assertEqual(len(socket_io_client1.get_received(self.events_namespace)), 1)
            self.assertEqual(len(socket_io_client2.get_received(self.events_namespace)), 1)
            self.assertEqual(len(socket_io_client3.get_received(self.events_namespace)), 0)
