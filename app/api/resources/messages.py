from flask_restful import Resource
from flask_restful import reqparse
from flask_restful import marshal_with, fields
from flask_restful import abort
from flask import g
from flask import request
from app.chats.models import Message
from app.api.decorators import basic_or_bearer_authorization_required as authorization_required
from app import db
from app.api.utils import abort_if_not_a_participant, return_chat_or_abort, return_message_or_abort, \
    abort_if_not_from_a_chat, abort_if_not_own
from app.api.utils import model_filter_by_get_params
from typing import Tuple, Any

message_fields = {
    'message_id': fields.Integer,
    'datetime_writing': fields.DateTime(),
    'text': fields.String,
    'sender_id': fields.Integer,
    'receiver_id': fields.Integer,
}

messages_list_fields = {
    'current_user_id': fields.Integer,
    'current_chat_id': fields.Integer,
    'data': fields.List(fields.Nested(message_fields)),
}

message_single_fields = {
    'current_user_id': fields.Integer,
    'current_chat_id': fields.Integer,
    'data': fields.Nested(message_fields),
}


def longer_than_zero(value: Any) -> str:
    """Custom input validator for flask_restful.reqparse.RequestParser. Converts given value into str, then - checks
    whether its length is equal to zero. If it is true - ValueError. So, api users cannot send a message without some
    text.
    :param value: a value from the request parser
    :type value: Any
    :returns: converted into a string value, if it is valid
    :rtype: str"""
    value = str(value)
    if len(value) == 0:
        raise ValueError("Message text length cannot be equal to zero")
    return value


class ChatMessagesList(Resource):
    @authorization_required
    @marshal_with(messages_list_fields)
    def get(self, chat_id: int) -> Tuple[dict, int]:
        """Returns the list of messages from given chat"""
        current_user_id = g.user.user_id
        chat = return_chat_or_abort(chat_id)
        abort_if_not_a_participant(current_user_id, chat)
        messages = Message.query.filter_by(chat_id=chat_id)
        messages = model_filter_by_get_params(Message, messages, request.args)
        return {'current_user_id': current_user_id, 'current_chat_id': chat_id, 'data': messages}, 200

    @authorization_required
    def post(self, chat_id: int) -> Tuple[dict, int]:
        """Allows to send one or more messages in given chat from the authenticated user"""
        current_user_id = g.user.user_id
        chat = return_chat_or_abort(chat_id)
        abort_if_not_a_participant(current_user_id, chat)
        parser = reqparse.RequestParser()
        parser.add_argument('texts', type=longer_than_zero, action='append', required=True)
        args = parser.parse_args()
        if args['texts']:
            user1_id, user2_id = chat.user1_id, chat.user2_id
            receiver_id = user2_id if user1_id == current_user_id else user1_id
            for text in args['texts']:
                message = Message(text=text, sender_id=current_user_id, receiver_id=receiver_id, chat_id=chat_id)
                db.session.add(message)
            db.session.commit()
            return {'current_user_id': current_user_id, 'current_chat_id': chat_id,
                    'message': f"Your message{'s were' if len(args['texts']) > 1 else ' was'} successfully sent"}, 201
        else:
            abort(400, message='It is necessary to put at least one message text')


class ChatMessageSingle(Resource):
    @authorization_required
    @marshal_with(message_single_fields)
    def get(self, chat_id: int, message_id: int) -> Tuple[dict, int]:
        """Return info about a certain message from the chat"""
        current_user_id = g.user.user_id
        chat = return_chat_or_abort(chat_id)
        abort_if_not_a_participant(current_user_id, chat)
        message = return_message_or_abort(message_id)
        abort_if_not_from_a_chat(chat_id, message)
        return {'current_user_id': current_user_id, 'current_chat_id': chat_id, 'data': message}, 200

    @authorization_required
    def delete(self, chat_id: int, message_id: int) -> Tuple[dict, int]:
        """Delete the message with a given id from the chat"""
        current_user_id = g.user.user_id
        chat = return_chat_or_abort(chat_id)
        abort_if_not_a_participant(current_user_id, chat)
        message = return_message_or_abort(message_id)
        abort_if_not_from_a_chat(chat_id, message)
        abort_if_not_own(current_user_id, message)
        db.session.delete(message)
        db.session.commit()
        return {'current_user_id': current_user_id, 'current_chat_id': chat_id,
                'message': f'Message {message_id} was successfully deleted'}, 200

    @authorization_required
    def put(self, chat_id: int, message_id: int) -> Tuple[dict, int]:
        """Updates the certain message text"""
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=longer_than_zero, required=True)
        args = parser.parse_args()
        current_user_id = g.user.user_id
        chat = return_chat_or_abort(chat_id)
        abort_if_not_a_participant(current_user_id, chat)
        message = return_message_or_abort(message_id)
        abort_if_not_from_a_chat(chat_id, message)
        abort_if_not_own(current_user_id, message)
        message.text = args.get('text')
        db.session.commit()
        return {'current_user_id': current_user_id, 'current_chat_id': chat_id,
                'message': f'Message {message_id} was successfully updated'}, 200
