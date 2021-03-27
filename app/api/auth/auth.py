from flask import jsonify, request, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity, jwt_required, get_jwt_claims
)

import requests

from app import jwt, db
from app.api import bluePrint
from app.models import Teacher, User
from .auth_utils import add_token_to_db, is_token_revoked, logout_user, jwt_roles_required


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

    teacher = Teacher.query.filter(Teacher.deleted == False).filter(
        (Teacher.phone == phone) | (Teacher.email == email)).first()
    additional_claims = {'client': 0}
    if teacher.check_password(password):
        access_token = create_access_token(identity=teacher.to_dict(), user_claims=additional_claims)
        refresh_token = create_refresh_token(identity=teacher.to_dict(), user_claims=additional_claims)
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
def refresh_access_token():
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
    current_user = get_jwt_identity()
    logout_user(current_user.get('id'))
    return jsonify(message="Token revoked."), 200


# -------------------Wechat APIs--------------------------------------------------------
@bluePrint.route('/wechat/login', methods=['POST'])
def wechat_login():
    """
    This api logins a user through wechat app.
    """
    code = request.json['code']

    wechat_code2session_url = 'https://api.weixin.qq.com/sns/jscode2session'
    payload = {
        'appid': current_app.config['WECHAT_APPID'],
        'secret': current_app.config['WECHAT_APP_SECRET'],
        'js_code': code,
        'grant_type': 'authorization_code'
    }
    r = requests.get(wechat_code2session_url, params=payload)
    openid = r.json()['openid']
    session_key = r.json()['session_key']
    # First check if the openID already exist in the DB.
    already_existed = User.query.filter(User.deleted == False).filter(
        User.openID == openid).first()
    additional_claims = {'client': 1}
    if already_existed:
        already_existed.sessionKey = session_key
        access_token = create_access_token(identity=already_existed.to_dict(), user_claims=additional_claims)
        refresh_token = create_refresh_token(identity=already_existed.to_dict(), user_claims=additional_claims)
        ret = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        add_token_to_db(access_token, current_app.config['JWT_IDENTITY_CLAIM'])
        add_token_to_db(refresh_token, current_app.config['JWT_IDENTITY_CLAIM'])

        db.session.add(already_existed)
        db.session.commit()
        return jsonify(ret), 201

    else:
        user = User()
        user.openID = openid
        user.sessionKey = session_key

        access_token = create_access_token(identity=user.to_dict(), user_claims=additional_claims)
        refresh_token = create_refresh_token(identity=user.to_dict(), user_claims=additional_claims)
        ret = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        add_token_to_db(access_token, current_app.config['JWT_IDENTITY_CLAIM'])
        add_token_to_db(refresh_token, current_app.config['JWT_IDENTITY_CLAIM'])
        db.session.add(user)
        db.session.commit()

        return jsonify(ret), 201


@bluePrint.route('/auth/wechat_test', methods=['get'])
@jwt_required
def wechat_test():
    """
    This API revokes all the tokens including access and refresh tokens that belong to the user.
    """
    claims = get_jwt_claims().get('client')
    user_id = get_jwt_identity()
    print(claims)
    print(type(claims))
    print(user_id.get('id'))
    return jsonify(message="test!!!"), 200


@bluePrint.route('/auth/roles_test', methods=['get'])
@jwt_roles_required(3)
def roles_test():
    """
    This API revokes all the tokens including access and refresh tokens that belong to the user.
    """
    print("authorized")
    return jsonify(message="test!!!"), 200
