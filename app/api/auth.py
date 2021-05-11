from flask_restful import Resource
from flask_restful import abort
from flask_restful import reqparse
from flask import g
from flask import current_app
from flask import render_template
from app.authentication.models import User
from app.authentication.validators import validate_length, validate_email, validate_password_length
from app.authentication.exceptions import ValidationError
from app import db
from .decorators import basic_or_bearer_authorization_required as authorization_required
from itsdangerous import SignatureExpired, BadSignature


class Register(Resource):
    def post(self):
        """Simple registration route. Any user can put his credentials and receive an answer. If everything is alright,
        the user will be registered by system"""
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        email = args.get('email')
        username = args.get('username')
        name = args.get('name')
        password = args.get('password')
        try:
            validate_email(email)
            validate_length(username, 3, 25, error_message='Username length must be between 3 and 25 chars')
            validate_length(name, 3, 25, error_message='Name length must be between 3 and 25 chars')
            validate_password_length(password)
        except ValidationError as e:
            abort(400, message=e.message)
        if User.query.filter_by(email=email).first():
            abort(400, message=f"User '{email}' has been registered!")
        elif User.query.filter_by(username=username).first():
            abort(400, message=f"Username '{username}' is busy! Try putting another one")
        else:
            user = User(email=email, username=username, name=name)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return {'message': 'Successfully registered!'}, 201


class Token(Resource):
    @authorization_required
    def get(self):
        """In order not to put username and password every requests, user can receive this authentication token.
        All the time before the token's revocation system is able to recognize a certain user without a credentials.
        So, user can get his own token by requesting this route"""
        token = g.user.get_authentication_token()
        expires_in = current_app.config['AUTHENTICATION_TOKEN_DEFAULT_EXPIRES_IN']
        return {'token': token, 'expires_in': expires_in}


class ForgotPassword(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True)
        args = parser.parse_args()
        email = args.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            user.send_email('Flask simple chats reset password',
                            render_template('authentication/emails/reset_password_rest.txt',
                                            user=user, token=user.get_reset_password_token()))
            return {'message': 'Check Your e-email to reset the password!'}, 200
        else:
            abort(400, message=f"User with e-mail '{email}' does not exist")


class ResetPassword(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('token', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        user = None
        try:
            user = User.get_user_by_reset_password_token(args.get('token'))
        except SignatureExpired:
            abort(400, message='Reset password token has expired. Use a new one')
        except BadSignature:
            abort(400, message='Reset password token is not valid')
        password = args.get('password')
        try:
            validate_password_length(password)
        except ValidationError as e:
            abort(400, message=e.message)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return {'email': user.email, 'message': "Successfully reset"}, 202


class Update(Resource):
    @authorization_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str)
        parser.add_argument('name', type=str)
        args = parser.parse_args()
        user = g.user
        username = args.get('username')
        name = args.get('name')
        username = None if username == user.username else username
        name = None if name == user.name else name
        if username:
            if User.query.filter_by(username=username).first():
                abort(400, message=f"Username '{username}' is busy! Try putting another one")
            else:
                try:
                    validate_length(username, 3, 25, error_message='Username length must be between 3 and 25 chars')
                    user.username = username
                except ValidationError as e:
                    abort(400, message=e.message)
        if name:
            try:
                validate_length(name, 3, 25, error_message='Name length must be between 3 and 25 chars')
                user.name = name
            except ValidationError as e:
                abort(400, message=e.message)
        db.session.add(user)
        db.session.commit()
        result = {}
        if username:
            result['username'] = username
        if name:
            result['name'] = name
        if len(result) > 0:
            result['message'] = 'Successfully updated'
            return result, 202
        else:
            result['message'] = 'Nothing was updated'
            return result, 400
