"""Base config module"""
import os


class Config:
    """
    Contains mostly development settings and their default conditions.
    To use on production, extremely sensitive values must be
    replaced with other ones from environment variables or from :file:`../instance/production_config.py`
    """
    SECRET_KEY = os.getenv('SECRET_KEY') or 'development'
    SEND_FILE_MAX_AGE_DEFAULT = 0
    DEBUG = True
    DB_USERNAME = os.getenv('DB_USERNAME') or 'postgres'
    DB_PASSWORD = os.getenv('DB_PASSWORD') or 'postgres'
    DB_HOST = os.getenv('DB_HOST') or '0.0.0.0'
    DB_PORT = os.getenv('DB_PORT') or '5432'
    DB_NAME = os.getenv('DB_NAME') or 'flask-simple-chats'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    MAIL_SERVER = os.getenv('EMAIL_HOST') or 'smtp.gmail.com'
    MAIL_PORT = os.getenv('EMAIL_PORT') or '587'
    MAIL_USERNAME = os.getenv('EMAIL_USER')
    MAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    MAIL_USE_TLS = True
    MAIL_DEFAULT_SENDER = MAIL_USERNAME or 'flask-simple-chats'
    PASSWORD_DEFAULT_EXPIRES_IN = 1800
    REQUIRED_MIN_PASSWORD_LENGTH = 8
    CHATS_PER_PAGE = 8
    MESSAGES_PER_LOAD_EVENT = 10
    AUTHENTICATION_TOKEN_DEFAULT_EXPIRES_IN = 3600
    BUNDLE_ERRORS = True


class TestConfig(Config):
    """
    Declares specific settings for testing.
    Likely, you want to involve exactly sqlite database, so it will be created in a temporary path to prevent from
    checking in.
    """
    TESTING = True
    TEST_DB_PATH = os.getenv('TEST_DB_PATH') or '/tmp'
    TEST_DB_NAME = os.getenv('TEST_DB_NAME') or 'chats_test_db.sqlite'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(TEST_DB_PATH, TEST_DB_NAME)}'
    WTF_CSRF_ENABLED = False
