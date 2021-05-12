from flask_restful import Resource
from flask_restful import fields, marshal_with
from flask import g
from flask import request
from app import db
from app.authentication.models import User
from app.api.decorators import basic_or_bearer_authorization_required as authorization_required
from app.api.utils import return_user_or_abort
from app.api.utils import model_filter_by_get_params

user_fields = {
    'user_id': fields.Integer,
    'username': fields.String,
    'name': fields.String,
    'date_joined': fields.DateTime()
}
users_list_fields = {
    'user_id': fields.Integer,
    'data': fields.List(fields.Nested(user_fields)),
}
user_single_fields = {
    'user_id': fields.Integer,
    'data': fields.Nested(user_fields),
}


class UsersList(Resource):
    @authorization_required
    @marshal_with(users_list_fields)
    def get(self):
        users = db.session.query(User.user_id, User.username, User.name, User.date_joined)
        users = model_filter_by_get_params(User, users, request.args)
        return {'user_id': g.user.user_id, 'data': users}, 200


class UserSingle(Resource):
    @authorization_required
    @marshal_with(user_single_fields)
    def get(self, user_id: int):
        user = return_user_or_abort(user_id)
        return {'user_id': g.user.user_id, 'data': user}
