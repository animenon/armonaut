# Copyright (C) 2017 Seth Michael Larson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import os
from flask import Flask, make_response, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, DateTime

__version__ = '1.0.0b1'


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
    from armonaut.index.controllers import index
    from armonaut.api.controllers import api
    from armonaut.oauth import oauth
    from armonaut.webhook import webhooks

    app.register_blueprint(index)
    app.register_blueprint(api)
    app.register_blueprint(oauth)
    app.register_blueprint(webhooks)
