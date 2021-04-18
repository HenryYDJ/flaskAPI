from flask import jsonify, request
from app.api import bluePrint
from app.api.auth.auth_utils import jwt_roles_required
from app.utils.utils import Roles


@bluePrint.route('/util/coverpic', methods=['POST'])
@jwt_roles_required(Roles.ADMIN)
def add_cover_pic():
    """
    This API adds a cover picture.
    """
    return jsonify(message="Picture added"), 201
