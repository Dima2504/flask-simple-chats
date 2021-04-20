import unittest
from flask import current_app
from app.config import TestConfig
from app import make_app
import os


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

    def test_instance_folder_exists(self):
        self.assertTrue(os.path.exists(self.app.instance_path))

    def test_testing_db_exists(self):
        self.assertTrue(os.path.exists(os.path.join(self.app.config['TEST_DB_PATH'], self.app.config['TEST_DB_NAME'])))


