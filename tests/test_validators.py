import unittest
import random
from app import make_app
from app.config import TestConfig
from app.authentication.exceptions import ValidationError
from app.authentication.validators import validate_password_length, validate_equal_passwords, validate_email
from app.authentication.validators import validate_length
import os


class ValidatorsTestCase(unittest.TestCase):
    """Tests implemented validators. Here there is no need to execute setUp and tearDown wrapping all the tests.
    So, there is only one initialization"""
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = make_app(TestConfig)
        cls.min_password_length = random.randint(1, 20)
        cls.app.config['REQUIRED_MIN_PASSWORD_LENGTH'] = cls.min_password_length
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app_context.pop()

    def test_validate_equal_passwords(self):
        for _ in range(3):
            with self.assertRaises(ValidationError):
                validate_equal_passwords(os.urandom(10).decode('latin1'), os.urandom(10).decode('latin1'))
        try:
            validate_equal_passwords('am i strong?', 'am i strong?')
            validate_equal_passwords('just simple test', 'just simple test')
            validate_equal_passwords('good bye;', 'good bye;')
        except ValidationError:
            self.fail('ValidationError must not have been raised')

    def test_validate_password_length_without_default_value(self):
        """Randint generate integer including both end points, so, it is necessary to subtract one from
        :attr:`min_password_length`"""
        for _ in range(3):
            with self.assertRaises(ValidationError):
                test_password = os.urandom(random.randint(0, self.min_password_length-1)).decode('latin1')
                validate_password_length(test_password)
        try:
            for _ in range(3):
                test_password = os.urandom(random.randint(self.min_password_length, 30)).decode('latin1')
                validate_password_length(test_password)
        except ValidationError:
            self.fail('ValidationError must not have been raised')

    def test_validate_password_length_with_default_value(self):
        for _ in range(3):
            with self.assertRaises(ValidationError):
                min_length = random.randint(1, 20)
                test_password = os.urandom(random.randint(0, min_length-1)).decode('latin1')
                validate_password_length(test_password, min_length)
        try:
            for _ in range(3):
                min_length = random.randint(1, 20)
                test_password = os.urandom(random.randint(min_length, 30)).decode('latin1')
                validate_password_length(test_password, min_length)
        except ValidationError:
            self.fail('ValidationError must not have been raised')

    def test_validate_email(self):
        valid_emails = ['dprice@msn.com', 'staikos@optonline.net', 'psharpe@mac.com', 'andale@yahoo.com', 'magusnet@icloud.com', 'hillct@verizon.net', 'dunstan@att.net', 'tmccarth@sbcglobal.net', ]
        invalid_emails = ["", "  ", "foo", "bar.dk", "foo@", "@bar.dk", "foo@bar", "foo@bar.ab12", "foo@.bar.ab", "foo.@bar.co", "foo@foo@bar.co", "fo o@bar.co", "foo@bar.dk", "123@bar.dk", "foo@456. dk", "f oo@bar456.info", "fvoo@bücher .中国"]
        for email in invalid_emails:
            with self.assertRaises(ValidationError):
                validate_email(email)
        try:
            for email in valid_emails:
                validate_email(email)
        except ValidationError:
            self.fail('ValidationError must not have been raised')

    def test_validate_length(self):
        with self.assertRaises(ValidationError):
            validate_length('test', 5, 6)
        with self.assertRaises(ValidationError):
            validate_length('test', 2, 3)
        with self.assertRaises(ValidationError):
            validate_length('test', 7, 9)
        with self.assertRaises(ValidationError):
            validate_length('test', 1, 2)
        try:
            validate_length('test', 4, 5)
            validate_length('test', 2, 4)
            validate_length('test', 4, 4)
        except ValidationError:
            self.fail('ValidationError must not have been raised')
        try:
            validate_length('t', 3, 4)
        except ValidationError as e:
            self.assertEqual(e.message, 'The given string is not match the necessary length')
        error_message = 'I am stupid error'
        try:
            validate_length('t', 3, 4, error_message)
        except ValidationError as e:
            self.assertEqual(e.message, error_message)

    def test_validation_error(self):
        error = ValidationError('Test case')
        self.assertTrue(isinstance(error, ValueError))
        self.assertTrue(hasattr(error, 'message'))
        self.assertEqual(error.message, 'Test case')
