import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer


db = SQLAlchemy()


class BaseModel(db.Model):
    id = Column(Integer, primary_key=True)


def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])

    db.init_app(app)

    return app
