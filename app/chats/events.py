from .. import socket_io
from flask import session
from flask import current_app
from flask_socketio import emit, join_room, leave_room
from flask_socketio import Namespace
from app.chats.models import Message
from app.authentication.models import User
from sqlalchemy import desc, or_, and_
from app import db
from datetime import datetime


class ChatRoomNamespace(Namespace):
    def on_connect(self):
        """Returns information about successful connection"""
        emit('status', {'message': 'connected'}, broadcast=False)

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
        current_user_id = session.get('current_user_id')
        companion_id = session.get('companion_id')
        if not User.is_chat_between(current_user_id, companion_id):
            User.create_chat(current_user_id, companion_id)
        m = Message(datetime_writing=datetime.utcfromtimestamp(data['timestamp_milliseconds'] / 1000),
                    text=data['message'],
                    sender_id=current_user_id,
                    receiver_id=companion_id)
        db.session.add(m)
        db.session.commit()

    def on_leave_room(self):
        """Sent by client when it leaves the room. Remove variables from user session, leaves room and sends
        status message for debug."""
        room_name = session.get('room_name')
        user_name = session.get('user_name')
        leave_room(room_name)
        emit('status', {'message': f'{user_name} left the room'}, room=room_name)

    def on_get_more_messages(self, data: dict):
        """
        Receives from a client offset and limit numbers and return prepared list with messages to load, if user scrolls
        up. The idea takes after typical ajax requests but here sockets are used.
        Emits json which contains descending messages from current user and companion's chat with given offset and limit
        from config. For each message there is an information if the owner is the current user.
        :param data: json, contains messages_offset number
        :type data: dict
        """
        messages_offset = data['messages_offset']
        messages_limit = current_app.config['MESSAGES_PER_LOAD_EVENT']
        current_user_id = session.get('current_user_id')
        companion_id = session.get('companion_id')
        last_messages = db.session.query(Message.sender_id, Message.text, Message.datetime_writing).filter(
            or_(and_(Message.sender_id == current_user_id, Message.receiver_id == companion_id),
                and_(Message.receiver_id == current_user_id, Message.sender_id == companion_id))).order_by(
            desc(Message.datetime_writing)).offset(messages_offset).limit(messages_limit).all()
        result_data = {'messages_number': len(last_messages),
                       'messages': [{'is_current_user': current_user_id == message[0],
                                     'message_text': message[1],
                                     'timestamp_milliseconds': message[2].timestamp() * 1000,
                                     } for message in last_messages]
                       }
        emit('load_more_messages', result_data, broadcast=False)


socket_io.on_namespace(ChatRoomNamespace('/chats/going'))
