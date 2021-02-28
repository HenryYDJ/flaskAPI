from flask import Blueprint

bluePrint = Blueprint('api', __name__)

from app.api import course, student, teacher, user, auth, wechat