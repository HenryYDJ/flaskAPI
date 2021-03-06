from datetime import datetime
from flask import Blueprint, jsonify, request
from flask.globals import current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db
from app.models import User
from app.api import bluePrint
from app.api.auth.auth_utils import jwt_roles_required
from app.dbUtils.dbUtils import query_existing_phone_user, query_existing_teacher,\
    query_validated_user, query_existing_user,\
    query_unvalidated_users, query_unrevoked_admins
from app.utils.utils import Roles, VALIDATIONS

#-----------------------Users Section-----------------------------------------
@bluePrint.route('/user', methods=['POST'])
def add_user():
    """
    This api is used from the web end point to initially register an user to the DB.
    """
    phone = request.json.get('phone', None)
    real_name = request.json.get('real_name', None)

    already_existed = query_existing_phone_user(phone)
    if already_existed:
        return jsonify(message='The phone number is already used.'), 409
    else:
        user = User()
        user.phone = phone
        user.real_name = real_name
        user.set_pwhash(request.json.get('password', None))
        user.register_time = datetime.utcnow()

        db.session.add(user)
        db.session.commit()
        return jsonify(message="User created successfully"), 201


@bluePrint.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    """
    This api gets one user from the DB by the access token.
    """
    id = get_jwt_identity().get('id')
    user = query_existing_user(id)    
    
    if user:
        result = user.full_info()
        if current_app.config.get('SUPER_ID') and user.openid == current_app.config.get("SUPER_ID"):
            result['is_super'] = True
        return jsonify(message=result), 201
    else:
        return jsonify(message="User not found"), 201


@bluePrint.route('/user_role', methods=['POST'])
@jwt_roles_required(Roles.ADMIN)
def assign_role():
    """
    This API assigns one role to the user in the request
    """
    user_id = request.json.get('user_id', None)
    role = request.json.get('role', None)

    user = query_validated_user(user_id)

    if user:
        user.role = role
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User role assigned"), 201
    else:
        return jsonify(message="User does not exist"), 400


@bluePrint.route('/validate_user', methods=['POST'])
@jwt_roles_required(Roles.ADMIN)  # Only Admin can validate a user
def validate_user():
    """
    This API validates the user in the request
    """
    user_id = request.json.get('user_id', None)
    decision = request.json.get('decision', None)

    user = query_existing_user(user_id)

    if user:
        user.validated = decision
        user.approver_id = get_jwt_identity().get('id')
        user.approve_time = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User validation status changed"), 201
    else:
        return jsonify(message="User does not exist"), 201


@bluePrint.route('/unvalidated_users', methods=['GET'])
@jwt_roles_required(Roles.ADMIN)  # Only Admin can get this list.
def get_unvalidated_users():
    """
    This API gets a list of all existing but unvalidated users from the DB.
    """
    users = query_unvalidated_users()

    if users:
        return jsonify(message=[user.validate_info() for user in users]), 201
    else:
        return jsonify(message="No unvalidated users"), 400


@bluePrint.route('/wechat_user_role', methods=['GET'])
@jwt_required()
def get_user_role():
    """
    This API returns the user's role and validation status.
    """
    user_id = get_jwt_identity().get('id')
    user = query_existing_user(user_id)

    if user:
        return jsonify(message=user.get_roles()), 201
    else:
        return jsonify(message="No such user."), 400


@bluePrint.route('/add_admin', methods=['POST'])
@jwt_roles_required(Roles.EVERYBODY)
def add_admin():
    """
    This API registers an admin
    """
    user_id = get_jwt_identity().get('id')
    user = query_existing_user(user_id)

    if user:
        user.roles = Roles.ADMIN
        user.avatar = request.json.get('avatar', None)
        user.phone = request.json.get('phone', None)
        user.gender = request.json.get('gender', None)
        user.real_name = request.json.get('real_name', None)
        user.language = request.json.get('language', 'CN')
        user.province = request.json.get('province', None)
        user.city = request.json.get('city', None)
        user.register_time = datetime.utcnow()
        user.nick_name = request.json.get('nick_name', None)
        user.validated = VALIDATIONS.WAITING

        db.session.add(user)
        db.session.commit()
        return jsonify(message="Admin added!"), 201
    else:
        return jsonify(message="No such user"), 201


@bluePrint.route('/validate_admin', methods=['POST'])
@jwt_required()  # Only a super can approve an admin
def validate_admin():
    """
    This API validates an admin in the request
    """
    super_id = get_jwt_identity().get('id')

    super = query_existing_user(super_id)

    if current_app.config.get('SUPER_ID') and super.openid == current_app.config.get('SUPER_ID'):
        admin_id = request.json.get('admin_id', None)
        decision = request.json.get('decision', 0)
        admin = query_existing_user(admin_id)
        if admin:
            admin.validated = decision
            admin.approver_id = super_id
            admin.approve_time = datetime.utcnow()
            db.session.add(admin)
            db.session.commit()
            return jsonify(message="Admin validation status changed by the man"), 201
        else:
            return jsonify(message="No such user"), 201
    else:
        return jsonify(message="What are you thinking?"), 201


@bluePrint.route('/get_admins', methods=['GET'])
@jwt_required()  # Only the super can get the admin list
def get_admins():
    """
    This API gets all admins in the DB
    """
    super_id = get_jwt_identity().get('id')

    super = query_existing_user(super_id)

    if current_app.config.get('SUPER_ID') and super.openid == current_app.config.get('SUPER_ID'):
        admins = query_unrevoked_admins()
        return jsonify(message=[admin.validate_info() for admin in admins]), 201
    else:
        return jsonify(message="What are you thinking?"), 201


@bluePrint.route('/get_approvees', methods=['POST'])
def get_approvees():
    """
    This api gets all approved user by user_id
    """
    user_id = request.json.get('user_id', None)

    user = query_existing_user(user_id)
    print(user.approver)

    return jsonify(message="User does not exist"), 400
