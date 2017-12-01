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

    # GitHub OAuth Config
    GITHUB_URL = os.environ.get('GITHUB_URL', 'https://github.com').rstrip('/')
    GITHUB_API_URL = os.environ.get('GITHUB_API_URL', 'https://api.github.com').rstrip('/')
    GITHUB_OAUTH_ID = os.environ.get('GITHUB_OAUTH_ID')
    GITHUB_OAUTH_SECRET = os.environ.get('GITHUB_OAUTH_SECRET')

    # BitBucket OAuth Config
    BITBUCKET_URL = os.environ.get('BITBUCKET_URL', 'https://bitbucket.com').rstrip('/')
    BITBUCKET_API_URL = os.environ.get('BITBUCKET_API_URL', 'https://bitbucket.com/api').rstrip('/')
    BITBUCKET_OAUTH_ID = os.environ.get('BITBUCKET_OAUTH_ID')
    BITBUCKET_OAUTH_SECRET = os.environ.get('BITBUCKET_OAUTH_SECRET')

    # GitLab OAuth Config
    GITLAB_URL = os.environ.get('GITLAB_URL', 'https://gitlab.com').rstrip('/')
    GITLAB_API_URL = os.environ.get('GITLAB_API_URL', 'https://api.gitlab.com').rstrip('/')
    GITLAB_OAUTH_ID = os.environ.get('GITLAB_OAUTH_ID')
    GITLAB_OAUTH_SECRET = os.environ.get('GITLAB_OAUTH_SECRET')

    # Flask-Login config
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_PROTECTION = 'strong'

    # Flask-Limiter config
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_STRATEGY = 'fixed-window-elastic-expiry'  # Mitigates burst attacks


class ProductionConfig(Config):
    DEBUG = False
    REMEMBER_COOKIE_SECURE = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    RATELIMIT_ENABLED = False
    TESTING = True