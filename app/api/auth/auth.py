from flask import jsonify, request, current_app
from app.models import Teacher, TokenBlacklist
from app.api import bluePrint
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, jwt_refresh_token_required,
    get_jwt_identity, jwt_required, get_raw_jwt
)
from .auth_utils import add_token_to_db, is_token_revoked, revoke_token, prune_db, logout_user
from app import jwt

@jwt.token_in_blacklist_loader
def check_token_revoke_statue(decoded_token):
    return is_token_revoked(decoded_token)

@bluePrint.route('/auth/login', methods=['POST'])
def login_teacher():
    if not request.is_json:
        return jsonify(message="No JSON in request"), 400
    
    phone = request.json.get('phone', None)
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    teacher = Teacher.query.filter(Teacher.deleted==False).filter((Teacher.phone==phone)|(Teacher.email==email)).first()
    if teacher.check_password(password):
        access_token = create_access_token(identity=teacher.to_dict())
        refresh_token = create_refresh_token(identity=teacher.to_dict())
        ret = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        add_token_to_db(access_token, current_app.config['JWT_IDENTITY_CLAIM'])
        add_token_to_db(refresh_token, current_app.config['JWT_IDENTITY_CLAIM'])
        return jsonify(ret), 201
    else:
        return jsonify(message="Bad credentials"), 401

@bluePrint.route('/auth/refresh', methods=['POST'])
@jwt_refresh_token_required
def refrest_token():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    add_token_to_db(access_token, current_app.config['JWT_IDENTITY_CLAIM'])
    return jsonify({'access_token': access_token}), 201

@bluePrint.route('/auth/logout', methods=['DELETE'])
@jwt_required
def logout():
    """
    This API revokes all the tokens including access and refresh tokens that belong to the user.
    """
    identity_claim = current_app.config['JWT_IDENTITY_CLAIM']
    raw_jwt = get_raw_jwt()
    user_id = raw_jwt[identity_claim].get('id')
    logout_user(user_id)
    return jsonify(message="Token revoked."), 200