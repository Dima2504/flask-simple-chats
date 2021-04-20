"""Custom authentication exceptions"""


class UserNotFoundByIndexError(IndexError):
    """Raise when there is not saved user with given id"""
    pass
