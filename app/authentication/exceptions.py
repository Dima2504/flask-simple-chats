"""Custom authentication exceptions"""


class UserNotFoundByIndexError(IndexError):
    """Raise when there is not saved user with given id"""
    pass


class ValidationError(ValueError):
    """Raises when an error occurs during the validation form data"""
    def __init__(self, message, *args, **kwargs):
        self.message = message
        super().__init__(*args, **kwargs)
