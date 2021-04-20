from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from app.authentication.exceptions import UserNotFoundByIndexError


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
