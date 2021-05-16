"""Blueprint which performs registering new cli commands is created here. Such a way to organize code makes it
clearly to split application logic and understand it.
"""
import sys
import unittest

from flask import Blueprint
from flask import current_app

from . import logger

cli_commands = Blueprint('cli_commands', __name__, cli_group=None)


@cli_commands.cli.command('tests')
def tests_command():  # pragma: no cover
    """Run all the tests from here"""
    logger.info('Tests are starting')

    tests = unittest.TestLoader().discover('tests')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(tests)

    # during the tests the logger became disabled, so, depending on the variable, we change its status
    logger.disabled = not current_app.config.get('LOGGING', False)
    logger.info('Tests have finished')
    if result.wasSuccessful():
        logger.info('Tests were finished successfully')
        sys.exit(0)
    else:
        logger.warning('Tests were finished unsuccessfully')
        sys.exit(1)
