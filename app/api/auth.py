from flask_restful import Resource
from flask_restful import abort
from flask import request
from flask import g
from flask import current_app
from app.authentication.models import User
from app.authentication.validators import validate_length, validate_email, validate_password_length
from app.authentication.exceptions import ValidationError
from app import db
from .decorators import basic_or_bearer_authorization_required as authorization_required


class Register(Resource):
    def post(self):
        """Simple registration route. Any user can put his credentials and receive an answer. If everything is alright,
        the user will be registered by system"""
        email = request.json.get('email')
        username = request.json.get('username')
        name = request.json.get('name')
        password = request.json.get('password')
        try:
            validate_email(email)
            validate_length(name, 3, 25, error_message='Name length must be between 3 and 25 chars')
            validate_password_length(password)
        except ValidationError as e:
            abort(400, message=e.message)
        if User.query.filter_by(email=email).first():
            abort(400, message='User with such an email has been registered!')
        elif User.query.filter_by(username=username).first():
            abort(400, message='This username is busy! Try putting another one')
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
