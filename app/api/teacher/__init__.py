from flask import Blueprint

bluePrint = Blueprint("teacher", __name__)

from app.api.teacher import teacher