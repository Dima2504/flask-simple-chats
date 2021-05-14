"""Base config module"""
import logging.config
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

    LOGGING = True
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '[%(asctime)s] - %(name)s - %(levelname)s - %(message)s - [%(pathname)s:%(lineno)d]'
            },
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'standard',
                'filename': 'logs/app.log',
                'mode': 'a',
                'maxBytes': 10000000,
                'backupCount': 5,
            },
            'mail': {
                'class': 'logging.handlers.SMTPHandler',
                'level': 'ERROR',
                'mailhost': (MAIL_SERVER, MAIL_PORT),
                'fromaddr': MAIL_USERNAME,
                'toaddrs': [os.getenv('EMAIL', default='some_email@gmail.com'), MAIL_USERNAME],
                'subject': 'Houston, we have a problem!',
                'credentials': (MAIL_USERNAME, MAIL_PASSWORD),
                'secure': (),
            },
        },
        'loggers': {
            'app': {
                'level': 'INFO',
                'handlers': ['file', 'mail', ],
            },
            'app.api': {
                'level': 'INFO',
                'handlers': ['file', 'mail', ],
            },
            'app.authentication': {
                'level': 'INFO',
                'handlers': ['file', 'mail', ],
            },
            'app.chats': {
                'level': 'INFO',
                'handlers': ['file', 'mail', ],
            },
        },
    }

    @classmethod
    def configure_logging(cls):
        """Applies logging dict config and creates necessary directories if they do not exist"""
        os.makedirs('logs', exist_ok=True)
        try:
            logging.config.dictConfig(cls.LOGGING_CONFIG)
            logging.getLogger('app').info('Logging config was loaded')
        except AttributeError as error:
            raise RuntimeError('To configure logging you must first declare "LOGGING_CONFIG" variable') from error

    @classmethod
    def disable_configured_loggers(cls):
        """Disables all the configured here loggers. It is useful for testing"""
        if hasattr(cls, 'LOGGING_CONFIG'):
            loggers = getattr(cls, 'LOGGING_CONFIG').get('loggers')
            if loggers:
                logging.getLogger('app').info('Configured loggers are being disabled')
                for logger_name in loggers:
                    logging.getLogger(logger_name).disabled = True


class TestConfig(Config):
    """
    Declares specific settings for testing.
    Likely, you want to involve exactly sqlite database, so it will be created in a temporary path to prevent from
    checking in.
    """
    TESTING = True
    LOGGING = False
    TEST_DB_PATH = os.getenv('TEST_DB_PATH') or '/tmp'
    TEST_DB_NAME = os.getenv('TEST_DB_NAME') or 'chats_test_db.sqlite'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(TEST_DB_PATH, TEST_DB_NAME)}'
    WTF_CSRF_ENABLED = False
