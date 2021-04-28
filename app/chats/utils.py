import functools


@functools.lru_cache(maxsize=256)
def get_users_unique_room_name(username1: str, username2: str) -> str:
    """
    Makes unique room name for any two users. Usernames are unique, so, generated room name is unique for every couple
    of users. If usernames are given in different orders, result is the same.
    In order to prevent from frequent recalculations, lru_cache is used.
    Raises value error if usernames are equal.
    :param username1: first user's username
    :type username1: str
    :param username2: second user's username
    :type username2: str
    :return: prepared room's name
    :rtype: str
    """
    if username1 == username2:
        raise ValueError('Given usernames are equal but they cannot be')
    return '_'.join(sorted([username1.strip(), username2.strip()]))
