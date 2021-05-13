from datetime import datetime

from flask import jsonify, request

from flask_jwt_extended import get_jwt_identity

from app import db
from app.api import bluePrint
from app.api.auth.auth_utils import jwt_roles_required
from app.dbUtils.dbUtils import query_existing_user
from app.utils.utils import Roles


# -------------------Teachers Section--------------------------------------------------------
@bluePrint.route('/parent', methods=['POST'])
@jwt_roles_required(Roles.EVERYBODY)
def register_parent():
    """
    This api adds parent's real information to the DB.
    """
    parent_id = get_jwt_identity().get('id')

    parent = query_existing_user(parent_id)
    phone = request.json['phone']

    if parent:
        parent.phone = request.json.get('phone', None)
        parent.realName = request.json.get('realName', None)
        parent.gender = request.json.get('gender', None)
        parent.language = request.json.get('language', 'CN')
        parent.province = request.json.get('province', None)
        parent.city = request.json.get('city', None)
        parent.avatar = request.json.get('avatar', None)
        parent.roles = Roles.PARENT
        parent.register_time = datetime.utcnow()
        db.session.add(parent)
        db.session.commit()
        return jsonify(message="Parent created successfully"), 201
    else:
        return jsonify(message='User does not exist'), 409