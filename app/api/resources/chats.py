from flask_restful import Resource
from flask_restful import abort
from flask_restful import reqparse
from flask_restful import fields, marshal_with
from app.api.decorators import basic_or_bearer_authorization_required as authorization_required
from app.authentication.models import chats, User
from app.chats.exceptions import ChatAlreadyExistsError
from app.chats.models import Message
from app import db
from flask import g
from sqlalchemy import or_
from app.api.utils import return_user_or_abort, return_chat_or_abort, abort_if_not_a_participant

chat_fields = {
    'chat_id': fields.Integer,
    'user1_id': fields.Integer,
    'user2_id': fields.Integer,
}
chats_list_fields = {
    'user_id': fields.Integer,
    'data': fields.List(fields.Nested(chat_fields)),
}
chats_single_fields = {
    'user_id': fields.Integer,
    'data': fields.Nested(chat_fields),
}


class ChatsList(Resource):
    @authorization_required
    @marshal_with(chats_list_fields)
    def get(self):
        """Returns the list of current user's chats"""
        current_user_id = g.user.user_id
        result = db.session.query(chats).filter(
            or_(chats.c.user1_id == current_user_id, chats.c.user2_id == current_user_id)).all()
        return {'user_id': current_user_id, 'data': result}, 200

    @authorization_required
    def post(self):
        """Creates a new chat between the current user and the users with the given in json id"""
        parser = reqparse.RequestParser()
        parser.add_argument('companion_id', required=True, type=int, help='User\'s id to create a chat with')
        args = parser.parse_args()

        current_user_id = g.user.user_id
        user_id = args.get('companion_id')
        return_user_or_abort(user_id)
        try:
            User.create_chat(current_user_id, user_id)
        except ChatAlreadyExistsError:
            abort(400, message=f'Your chat with the user {user_id} already exists')
        db.session.commit()
        return {'user_id': current_user_id, 'companion_id': user_id,
                'chat_id': User.get_chat_id_by_users_ids(current_user_id, user_id),
                'message': 'Chat was successfully created'}, 201


class ChatSingle(Resource):
    @authorization_required
    @marshal_with(chats_single_fields)
    def get(self, chat_id: int):
        """Returns the certain chat with a given chat_id"""
        current_user_id = g.user.user_id
        chat = return_chat_or_abort(chat_id)
        abort_if_not_a_participant(current_user_id, chat)
        return {'user_id': current_user_id, 'data': chat}

    @authorization_required
    def delete(self, chat_id: int):
        """Deletes the certain chat with a given id."""
        current_user_id = g.user.user_id
        chat = return_chat_or_abort(chat_id)
        abort_if_not_a_participant(current_user_id, chat)
        Message.delete_messages(chat_id=chat_id)
        User.delete_chat(chat_id=chat_id)
        db.session.commit()
        return {'user_id': current_user_id, 'chat_id': chat_id, 'message': 'Chat was successfully deleted'}, 200
