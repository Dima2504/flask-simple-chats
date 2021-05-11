"""Custom exceptions to work with chats."""


class ChatNotFoundByIndexesError(IndexError):
    """Raises when there are no found chats by given users' ids"""
    pass


class ChatAlreadyExistsError(ValueError):
    """Raises when creating of new chat is not successful because the chat with given users ids already exists"""
    pass


class MessageNotFoundByIndexError(IndexError):
    """Is raised when there is no message by given id"""
    pass