from flask import Blueprint, jsonify, request
from app import db
from app.models import User, user_schema, users_schema
from app.api.user import bluePrint

#-----------------------Users Section-----------------------------------------
@bluePrint.route('/api/v1.0/user', methods=['POST'])
def add_user():
    """
    This api adds one user to the DB.
    """
    name = request.json['name']

    already_existed = User.query.filter_by(name=name, deleted=False).first()
    if already_existed:
        return jsonify(message='The user already exists'), 409
    else:
        user = User(name=name)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User created successfully"), 201


@bluePrint.route('/api/v1.0/user', methods=['GET'])
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


@bluePrint.route('/api/v1.0/users', methods=['GET'])
def get_users():
    """
    This api gets all users from the DB.
    """
    users = User.query.filter_by(deleted=False).all()
    if users:
        return jsonify(users_schema.dump(users))
    else:
        return jsonify(message="No users found"), 404


@bluePrint.route('/api/v1.0/user', methods=['PUT'])
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


@bluePrint.route('/api/v1.0/user', methods=['DELETE'])
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