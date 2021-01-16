from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager
import os

from config import Config

db = SQLAlchemy()
ma = Marshmallow()
login = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    ma.init_app(app)
    login.init_app(app)

    from app.api.student import bluePrint as student_bp
    app.register_blueprint(student_bp)

    from app.api.teacher import bluePrint as teacher_bp
    app.register_blueprint(teacher_bp)

    from app.api.course import bluePrint as course_bp
    app.register_blueprint(course_bp)

    from app.api.user import bluePrint as user_bp
    app.register_blueprint(user_bp)

    return app

from app import models