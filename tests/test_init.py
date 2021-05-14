import logging
import os
import unittest

from flask import current_app

from app import make_app
from app.config import TestConfig, Config


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

    def test_loggers_disable_status(self):
        flag = self.app.config['LOGGING']
        loggers = self.app.config['LOGGING_CONFIG'].get('loggers')
        if loggers:
            for logger_name in loggers:
                self.assertEqual(not flag, logging.getLogger(logger_name).disabled)

    def test_logs_folder_exists(self):
        self.assertTrue(os.path.exists('logs'))

    def test_configure_logging(self):
        logging_config = None
        if hasattr(Config, 'LOGGING_CONFIG'):
            logging_config = Config.LOGGING_CONFIG
            del Config.LOGGING_CONFIG
        with self.assertRaises(RuntimeError):
            Config.configure_logging()
        if logging_config:
            setattr(Config, 'LOGGING_CONFIG', logging_config)

    def test_disabled_configured_loggers(self):
        if 'LOGGING_CONFIG' in self.app.config:
            loggers = self.app.config['LOGGING_CONFIG'].get('loggers')
            if loggers:
                for logger_name in loggers:
                    logging.getLogger(logger_name).disabled = False
                TestConfig.disable_configured_loggers()
                for logger_name in loggers:
                    self.assertTrue(logging.getLogger(logger_name).disabled)
                # returns everything to the initial condition if it is necessary
                if self.app.config['LOGGING']:
                    for logger_name in loggers:
                        logging.getLogger(logger_name).disabled = False
