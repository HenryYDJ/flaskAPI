from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import os

from config import Config

db = SQLAlchemy()
ma = Marshmallow()
login = LoginManager()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    ma.init_app(app)
    login.init_app(app)
    migrate.init_app(app=app, db=db)
    jwt.init_app(app)

    from app.api import bluePrint
    app.register_blueprint(bluePrint, url_prefix='/api/v1.0')

    return app

from app import models