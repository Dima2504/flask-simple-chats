from .. import socket_io
from flask import session
from flask_socketio import emit, join_room, leave_room
from flask_socketio import Namespace
from app.chats.models import Message
from app import db
from datetime import datetime


class ChatRoomNamespace(Namespace):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_enter_room(self):
        """Is sent by client when it connects to the sever. Gets room name and user's name from the session and joins
        the room. Sends a message on status handler only for debug."""
        room_name = session.get('room_name')
        user_name = session.get('user_name')
        join_room(room_name)
        emit('status', {'message': f'{user_name} entered the room'}, room=room_name)

    def on_put_data(self, data: dict):
        """
        Receives message and time of writing, saves the message and redirects it into print_message handler on client.
        Broadcasts to all people in room (to the current user and to a companion).
        :param data: json from client which contains message and timestamp
        :type data: dict
        """
        room_name = session.get('room_name')
        emit('print_message', data, room=room_name)

        m = Message(datetime_writing=datetime.utcfromtimestamp(data['timestamp_milliseconds'] / 1000),
                    text=data['message'],
                    sender_id=session.get('current_user_id'),
                    receiver_id=session.get('companion_id'))
        db.session.add(m)
        db.session.commit()

    def on_leave_room(self):
        """Sent by client when it leaves the room. Remove variables from user session, leaves room and sends
        status message for debug."""
        room_name = session.get('room_name')
        user_name = session.get('user_name')
        leave_room(room_name)
        emit('status', {'message': f'{user_name} left the room'}, room=room_name)


socket_io.on_namespace(ChatRoomNamespace('/chats/going'))
