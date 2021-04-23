from app.authentication.exceptions import ValidationError
from email_validator import validate_email as val_em
from email_validator import EmailNotValidError
from flask import current_app


def validate_equal_passwords(password1: str, password2: str):
    """Compares two passwords and raises validation error if aren't equal"""
    if not password1 == password2:
        raise ValidationError("Given passwords don't match")


def validate_email(email: str):
    """Delegate all the responsibility into email validator library from PyPi"""
    try:
        val_em(email)
    except EmailNotValidError:
        raise ValidationError("E-mail is not valid")


def validate_password_length(password: str, min_length: int = None):
    """Validate if the password shorter than it must be
    :param password: given password
    :param min_length: required length of password"""
    if not min_length:
        min_length = current_app.config['REQUIRED_MIN_PASSWORD_LENGTH']
    if len(password) < min_length:
        raise ValidationError("Password if too short")
