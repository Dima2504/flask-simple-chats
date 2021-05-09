from app.authentication.exceptions import ValidationError
from email_validator import validate_email as val_em
from email_validator import EmailNotValidError
from flask import current_app


def validate_equal_passwords(password1: str, password2: str):
    """Compares two passwords and raises validation error if aren't equal"""
    if len(password1) != len(password2):
        raise ValidationError("Given passwords don't match")
    elif not password1 == password2:
        raise ValidationError("Given passwords don't match")


def validate_email(email: str):
    """Delegate all the responsibility into email validator library from PyPi"""
    try:
        val_em(email)
    except EmailNotValidError:
        raise ValidationError(f"E-mail '{email}' is not valid")


def validate_password_length(password: str, min_length: int = None):
    """Validate if the password shorter than it must be
    :param password: given password
    :param min_length: required length of password"""
    if not min_length:
        min_length = current_app.config['REQUIRED_MIN_PASSWORD_LENGTH']
    if len(password) < min_length:
        raise ValidationError("Password is too short")


def validate_length(string: str, min_length: int, max_length: int, error_message: str = None):
    """
    Validates if the given string length is between the obligatory edges
    :param string: string to check
    :type string: str
    :param min_length: minimal possible length
    :type min_length: int
    :param max_length: maximal possible length
    :type max_length: int
    :param error_message: message to be shown if the validations fails
    :type error_message: str
    """
    if not (min_length <= len(string) <= max_length):
        raise ValidationError(error_message or 'The given string is not match the necessary length')
