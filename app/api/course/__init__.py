from flask import Blueprint

bluePrint = Blueprint("course", __name__)

from app.api.course import course