import unittest
from flask import current_app
from app.config import TestConfig
from app import make_app


class InitTestCase(unittest.TestCase):
    """
    Tests for checking an initialization.
    """
    def setUp(self) -> None:
        self.app = make_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self) -> None:
        self.app_context.pop()

    def test_current_app(self):
        self.assertTrue(current_app is not None)

    def test_config(self):
        self.assertTrue(self.app.config['TESTING'])
