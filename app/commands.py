"""Blueprint which performs registering new cli commands is created here. Such a way to organize code makes it
clearly to split application logic and understand it.
"""
from flask import Blueprint

cli_commands = Blueprint('cli_commands', __name__, cli_group=None)


@cli_commands.cli.command('tests')
def tests_command():
    """Run all the tests from here"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner().run(tests)