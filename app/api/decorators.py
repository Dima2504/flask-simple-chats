"""Decorators for api views. Here is only one decorator which requires authorization"""
from functools import wraps

from flask import g
from flask import request
from flask_restful import abort
from itsdangerous import BadSignature, SignatureExpired
from sqlalchemy import or_

from app.authentication.models import User
from . import logger


def basic_or_bearer_authorization_required(func):
    """Restricts access only for users who represent their credentials username:password or their authentication token
    For now the decorator allows to use only two http authorization methods: basic, which is based on base64 encoding
    and bearer, which works through json web tokens"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        credentials = request.authorization
        if credentials:
            logger.info('User is trying to log in via basic auth')
            username_or_email = credentials.get('username')
            password = credentials.get('password')
            user = User.query.filter(or_(User.username == username_or_email, User.email == username_or_email)).first()
            if not user:
                logger.info('User was not found by email or username')
                abort(401, message='Wrong login! Maybe, you have not been registered')
            elif not user.verify_password(password):
                logger.info("User put the wrong password")
                abort(401, message='Wrong password! Try again')
            else:
                setattr(g, 'user', user)
                return func(*args, **kwargs)
        else:
            header = request.headers.get('Authorization')
            if header:
                logger.info('User is trying to log in via bearer auth')
                auth_type, token = header.split()
                if auth_type.lower() == 'bearer':
                    user = None
                    try:
                        user = User.get_user_by_authentication_token(token)
                    except SignatureExpired:
                        abort(401, message='Your authentication token period has expired')
                    except BadSignature:
                        abort(401, message='Authentication token is not valid')
                    setattr(g, 'user', user)
                    return func(*args, **kwargs)
        logger.info('User did not use any authentication')
        abort(403, message='To access use Basic (base64) or Bearer (jwt) http authorization')
    return wrapper
