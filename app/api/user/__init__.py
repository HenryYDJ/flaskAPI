from flask import Blueprint

bluePrint = Blueprint("user", __name__)

from app.api.user import user