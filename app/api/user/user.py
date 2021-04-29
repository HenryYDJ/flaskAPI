from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models import User, user_schema, users_schema
from app.api import bluePrint
from app.api.auth.auth_utils import jwt_roles_required
from app.dbUtils.dbUtils import query_existing_phone_user, query_validated_user, query_existing_user

#-----------------------Users Section-----------------------------------------
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

# TODO: finish this function, add the approver info and approve time to DB
# @bluePrint.route('/validate_user', methods=['POST'])
# @jwt_roles_required(Roles.ADMIN)
# def validate_user():
#     """
#     This API the user in the request
#     """
#     user_id = request.json.get('user_id', None)

#     user = query_existing_user(user_id)

#     if user:
#         user.role = role
#         db.session.add(user)
#         db.session.commit()
#         return jsonify(message="User role assigned"), 201
#     else:
#         return jsonify(message="User does not exist"), 400

@bluePrint.route('/user', methods=['POST'])
def add_user():
    """
    This api adds one user to the DB.
    """
    realName = request.json['realName']
    phone = request.json['phone']

    already_existed = query_existing_phone_user(phone)
    if already_existed:
        return jsonify(message='The user already exists'), 409
    else:
        user = User()
        user.phone = phone
        user.realName = realName
        user.set_pwhash(request.json.get('password', None))

        db.session.add(user)
        db.session.commit()
        return jsonify(message="User created successfully"), 201


@bluePrint.route('/user', methods=['GET'])
def get_user():
    """
    This api gets one user from the DB by the user's id.
    """
    id = request.args.get('user_id', None)

    user = User.query.filter_by(id=id, deleted=False).first()
    if user:
        return jsonify(user_schema.dump(user))
    else:
        return jsonify(message="User not found"), 404


@bluePrint.route('/users', methods=['GET'])
def get_users():
    """
    This api gets all users from the DB.
    """
    users = User.query.filter_by(deleted=False).all()
    if users:
        return jsonify(users_schema.dump(users))
    else:
        return jsonify(message="No users found"), 404


@bluePrint.route('/user', methods=['PUT'])
def update_user():
    """
    This api updates a user's information based on the user's id
    """
    id = request.args.get('user_id', None)

    user = User.query.filter_by(id=id, deleted=False).first()
    if user:
        user.name = request.json["name"]
        db.session.add(user)
        db.session.commit()
        return jsonify(user_schema.dump(user))
    else:
        return jsonify(message="User not found"), 404


@bluePrint.route('/user', methods=['DELETE'])
def delete_user(user_id):
    """
    This api deletes a user by user's id from the DB.
    """
    id = request.args.get('user_id', None)

    user = User.query.filter_by(id=id, deleted=False).first()
    if user:
        user.deleted = True
        db.session.add(user)
        db.session.commit()
        return jsonify(user_schema.dump(user))
    else:
        return jsonify(message="User not found"), 404