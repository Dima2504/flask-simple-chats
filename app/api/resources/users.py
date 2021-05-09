from flask_restful import Resource
from flask_restful import fields, marshal_with
from flask_restful import abort
from flask import g
from app import db
from app.authentication.models import User
from app.authentication.exceptions import UserNotFoundByIndexError
from app.api.decorators import basic_or_bearer_authorization_required as authorization_required

user_fields = {
    'user_id': fields.Integer,
    'username': fields.String,
    'name': fields.String,
    'date_joined': fields.DateTime()
}
users_list_fields = {
    'current_user_id': fields.Integer,
    'data': fields.List(fields.Nested(user_fields)),
}
user_single_fields = {
    'current_user_id': fields.Integer,
    'data': fields.Nested(user_fields),
}


class UsersList(Resource):
    @authorization_required
    @marshal_with(users_list_fields)
    def get(self):
        users = db.session.query(User.user_id, User.username, User.name, User.date_joined).all()
        return {'current_user_id': g.user.user_id, 'data': users}, 200


class UserSingle(Resource):
    @authorization_required
    @marshal_with(user_single_fields)
    def get(self, user_id: int):
        user = None
        try:
            user = User.get_user_by_id(user_id)
        except UserNotFoundByIndexError:
            abort(404, message=f'User {user_id} does not exist')
        return {'current_user_id': g.user.user_id, 'data': user}
