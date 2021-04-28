from .. import socket_io
from flask import session
from flask_socketio import emit, join_room, leave_room
from flask_socketio import Namespace


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
        Receives message and time of writing and redirects it into print message handler on client.
        Broadcasts to all people in room (to the current user and to a companion).
        :param data: json from client which contains message and timestamp
        :type data: dict
        """
        room_name = session.get('room_name')
        user_name = session.get('user_name')
        emit('print_message', {'message': data['message'], 'user_name': user_name}, room=room_name)

    def on_leave_room(self):
        """Sent by client when it leaves the room. Remove variables from user session, leaves room and sends
        status message for debug."""
        room_name = session.get('room_name')
        user_name = session.get('user_name')
        leave_room(room_name)
        emit('status', {'message': f'{user_name} left the room'}, room=room_name)


socket_io.on_namespace(ChatRoomNamespace('/chats/going'))
