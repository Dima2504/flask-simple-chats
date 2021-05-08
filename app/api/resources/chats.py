from flask_restful import Resource
from flask_restful import abort
from app.api.decorators import basic_or_bearer_authorization_required as authorization_required
from app.authentication.models import chats, User
from app.chats.exceptions import ChatAlreadyExistsError
from app.chats.models import Message
from app import db
from flask import g
from flask import request
from sqlalchemy import or_, exists


class Chats(Resource):
    @authorization_required
    def get(self, chat_id=None):
        current_user_id = g.user.user_id
        if not chat_id:
            result = db.session.query(chats).filter(
                or_(chats.c.user1_id == current_user_id, chats.c.user2_id == current_user_id)).all()

            return {'current_user_id': current_user_id, 'data': [row._asdict() for row in result]}, 200
        
        chat = db.session.query(chats).filter(chats.c.chat_id == chat_id).first()
        if not chat:
            abort(404, message='A chat with such an id is not found')
        chat = chat._asdict()
        if chat['user1_id'] != current_user_id and chat['user2_id'] != current_user_id:
            abort(403, message='You are not a participant of this chat.')
        return {'current_user_id': current_user_id, 'data': chat}

    @authorization_required
    def delete(self, chat_id=None):
        if not chat_id:
            abort(405)
        current_user_id = g.user.user_id
        chat = db.session.query(chats).filter(chats.c.chat_id == chat_id).first()
        if not chat:
            abort(404, message='A chat with such an id is not found')
        chat = chat._asdict()
        if chat['user1_id'] != current_user_id and chat['user2_id'] != current_user_id:
            abort(403, message='You are not a participant of this chat.')
        Message.delete_messages(chat_id=chat_id)
        User.delete_chat(chat_id=chat_id)
        db.session.commit()
        return {'current_user_id': current_user_id, 'message': 'Chat was successfully deleted'}, 200

    @authorization_required
    def post(self, chat_id=None):
        if chat_id:
            abort(405)
        data = request.json
        if not data or 'user_id' not in data:
            abort(400)
        current_user_id = g.user.user_id
        user_id = data['user_id']
        if not db.session.query(exists(User).where(User.user_id == user_id)).scalar():
            abort(400, message="A suggested user does not exist")
        try:
            User.create_chat(current_user_id, user_id)
        except ChatAlreadyExistsError:
            abort(400, message='Your chat with a suggested user already exists')
        db.session.commit()
        return {'current_user_id': current_user_id, 'message': 'Chat was successfully created'}, 201

