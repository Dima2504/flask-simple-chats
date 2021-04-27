from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from app.authentication.exceptions import UserNotFoundByIndexError
from itsdangerous import TimedJSONWebSignatureSerializer
from flask import current_app
from app.authentication.email import send_mail

chats = db.Table('chats',
                 db.Column('user1_id', db.Integer, db.ForeignKey('users.user_id')),
                 db.Column('user2_id', db.Integer, db.ForeignKey('users.user_id')),
                 db.PrimaryKeyConstraint('user1_id', 'user2_id'))


class User(db.Model):
    """
    Main user model with enabled password hashing and verifying
    """
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    data_joined = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    chats = db.relationship('User', secondary=chats,
                            primaryjoin=chats.c.user1_id == user_id,
                            secondaryjoin=chats.c.user2_id == user_id)

    def set_password(self, password: str):
        """Hashes user password using werkzeug method and saves it into the appropriate attribute"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        """Makes hash from given password and compares it with already existing one. Uses werkzeug method."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f'User - {self.username}'

    @classmethod
    def get_user_by_id(cls, user_id: int) -> 'User':
        """Return user with given id if exists, else - raise error"""
        user = cls.query.get(user_id)
        if not user:
            raise UserNotFoundByIndexError
        return user

    def send_email(self, subject: str, text: str):
        """Sends an e-mail with given subject and text to the current user"""
        send_mail(self.email, subject, text)

    def get_reset_password_token(self, expiration_period: int = None) -> str:
        """Generate web token with given expiration period and saves the current user's id in.
        Web signature is based on application secret key, so it must be saved from others.
        :param expiration_period: time in seconds which must go by before the token revocation.
        :type expiration_period: int
        :returns generated token
        :rtype str
        """
        if not expiration_period:
            expiration_period = current_app.config['PASSWORD_DEFAULT_EXPIRES_IN']
        secret_key = current_app.config['SECRET_KEY']
        serializer = TimedJSONWebSignatureSerializer(secret_key, expiration_period)
        token = serializer.dumps({'user_id': self.user_id}).decode()
        return token

    @classmethod
    def get_user_by_reset_password_token(cls, token: str) -> 'User':
        """Deserializes token with current app secret key and receives saved user's id.
        Function return a user with such an id
        :param token: Token received from password reset view
        :type token: str
        :returns: user with received id
        :rtype User
        """
        serializer = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        user_id = serializer.loads(token)['user_id']
        return cls.get_user_by_id(user_id)

    def create_chat(self, user: 'User') -> None:
        """Make two notes in chats table, so self-user and given user will be marked that they have chat together.
        It works bidirectionally, so we don't need to create chat from another side after creating once"""
        if user not in self.chats:
            self.chats.append(user)
            user.chats.append(self)

    def delete_chat(self, user: 'User') -> None:
        """Delete chat connection between self and given users. Works bidirectionally like a method above"""
        if user in self.chats:
            self.chats.remove(user)
            user.chats.remove(self)

    def is_chat(self, user: 'User') -> bool:
        """Checks is the current user and a given user have chat together"""
        return user in self.chats and self in user.chats
