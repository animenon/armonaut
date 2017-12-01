import datetime
import os
from flask import Flask, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import Column, Integer, DateTime


def limiter_key_func() -> str:
    """The Flask-Limiter key function. We delimit by remote address
    if the user isn't logged in, otherwise we delimit by their 
    current user id number."""
    if current_user.is_anonymous:
        return get_remote_address()
    else:
        return str(current_user.id)


db = SQLAlchemy()
login = LoginManager()
limiter = Limiter(key_func=limiter_key_func)


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    create_time = Column(DateTime, nullable=False,
                         default=datetime.datetime.utcnow)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])

    db.init_app(app)
    login.init_app(app)
    limiter.init_app(app)
    
    set_error_handlers(app)
    register_blueprints(app)

    return app


def set_error_handlers(app):
    """Creates all error handlers for a Flask
    application created in the factory.
    """
    @app.errorhandler(429)
    def ratelimit_handler(e):
        response = jsonify(message=f'Rate limit exceeded: {e.description} See '
                                    'https://armonaut.io/docs/rate-limit for more information')
        return make_response(response, 429)

    
def register_blueprints(app):
    """Registers all Blueprints for a Flask application
    created in the factory method.
    """
    from armonaut.api.controllers import api
    app.register_blueprint(api)
