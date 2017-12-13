import os
import tempfile


class Config(object):

    # Web Config
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ['SECRET_KEY']

    # PostgreSQL Config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgres://postgres:@localhost:5432/armonaut')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis Config
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # GitHub Config
    GITHUB_API_SECRET = os.environ.get('GITHUB_API_SECRET')
    GITHUB_OAUTH_ID = os.environ.get('GITHUB_OAUTH_ID')
    GITHUB_OAUTH_SECRET = os.environ.get('GITHUB_OAUTH_SECRET')

    # BitBucket Config
    BITBUCKET_API_SECRET = os.environ.get('BITBUCKET_API_SECRET')
    BITBUCKET_OAUTH_ID = os.environ.get('BITBUCKET_OAUTH_ID')
    BITBUCKET_OAUTH_SECRET = os.environ.get('BITBUCKET_OAUTH_SECRET')

    # GitLab Config
    GITLAB_API_SECRET = os.environ.get('GITLAB_API_SECRET')
    GITLAB_OAUTH_ID = os.environ.get('GITLAB_OAUTH_ID')
    GITLAB_OAUTH_SECRET = os.environ.get('GITLAB_OAUTH_SECRET')

    # Flask-Login config
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_PROTECTION = 'strong'

    # Flask-Limiter config
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_STRATEGY = 'fixed-window-elastic-expiry'


class ProductionConfig(Config):
    DEBUG = False
    REMEMBER_COOKIE_SECURE = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SERVER_NAME = 'localhost:8080'
    RATELIMIT_ENABLED = False


class TestingConfig(Config):
    TESTING = True
    SERVER_NAME = 'localhost:8080'
    RATELIMIT_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
