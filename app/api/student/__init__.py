from flask import Blueprint

bluePrint = Blueprint("student", __name__)

from app.api.student import student