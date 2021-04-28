import unittest
from app import make_app
from app.config import TestConfig
from app.chats.utils import get_users_unique_room_name as get_rn
import os


class UtilsTestCase(unittest.TestCase):
    """Tries out additional utils"""
    def setUp(self) -> None:
        get_rn.cache_clear()

    def tearDown(self) -> None:
        get_rn.cache_clear()

    def test_get_users_unique_room_name(self):
        usernames = [os.urandom(8).decode('latin1') for _ in range(3)]
        self.assertEqual(get_rn(usernames[0], usernames[1]), get_rn(usernames[1], usernames[0]))
        self.assertEqual(get_rn(usernames[1], usernames[2]), get_rn(usernames[2], usernames[1]))
        self.assertEqual(get_rn(usernames[0], usernames[2]), get_rn(usernames[2], usernames[0]))

        self.assertNotEqual(get_rn(usernames[0], usernames[1]), get_rn(usernames[1], usernames[2]))
        self.assertNotEqual(get_rn(usernames[1], usernames[2]), get_rn(usernames[0], usernames[2]))
        self.assertNotEqual(get_rn(usernames[0], usernames[1]), get_rn(usernames[0], usernames[2]))

        with self.assertRaises(ValueError):
            for i in range(3):
                get_rn(usernames[i], usernames[i])
