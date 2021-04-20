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


class TestConfig(Config):
    """
    Declares specific settings for testing.
    Likely, you want to involve exactly sqlite database, so it will be created in :path:`../instance` to prevent from
    checking in.
    """
    TESTING = True
    TEST_DB_PATH = os.getenv('TEST_DB_PATH') or '/tmp'
    TEST_DB_NAME = os.getenv('TEST_DB_NAME') or 'chats_test_db.sqlite'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(TEST_DB_PATH, TEST_DB_NAME)}'
