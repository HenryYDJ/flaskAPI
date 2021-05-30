from flask import jsonify, request, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt_identity, jwt_required
)

import requests

from app import jwt, db
from app.api import bluePrint
from app.models import User
from .auth_utils import add_token_to_db, is_token_revoked, logout_user, jwt_roles_required
from app.dbUtils.dbUtils import query_existing_phone_user, query_existing_openid_user

from app.models import ClassSession


@jwt.token_in_blocklist_loader
def check_token_revoke_status(jwt_headers, jwt_payload):
    return is_token_revoked(jwt_headers, jwt_payload)


@bluePrint.route('/auth/login', methods=['POST'])
def login_web():
    if not request.is_json:
        return jsonify(message="No JSON in request"), 400

    phone = request.json.get('phone', None)
    password = request.json.get('password', None)

    user = query_existing_phone_user(phone)
    if user:
        if user.check_password(password):
            access_token = create_access_token(identity=user.to_dict())
            refresh_token = create_refresh_token(identity=user.to_dict())
            ret = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            add_token_to_db(access_token, current_app.config['JWT_IDENTITY_CLAIM'])
            add_token_to_db(refresh_token, current_app.config['JWT_IDENTITY_CLAIM'])
            return jsonify(ret), 201
        else:
            return jsonify(message="Bad credentials"), 401
    else:
        return jsonify(message="Bad credentials"), 401


@bluePrint.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
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
def login_wechat():
    """
    This api logins a user through wechat app.
    """
    code = request.json.get('code', None)

    wechat_code2session_url = 'https://api.weixin.qq.com/sns/jscode2session'
    payload = {
        'appid': current_app.config['WECHAT_APPID'],
        'secret': current_app.config['WECHAT_APP_SECRET'],
        'js_code': code,
        'grant_type': 'authorization_code'
    }
    r = requests.get(wechat_code2session_url, params=payload)
    
    if "errcode" in str(r.content):
        return jsonify(message="Something wrong with the code"), 201

    openid = r.json().get('openid', None)
    session_key = r.json().get('session_key', None)

    # check if the openID already exists in the DB.
    user = query_existing_openid_user(openid)

    if not user:
        user = User()

    user.openID = openid
    user.sessionKey = session_key

    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.to_dict())
    refresh_token = create_refresh_token(identity=user.to_dict())
    ret = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    add_token_to_db(access_token, current_app.config['JWT_IDENTITY_CLAIM'])
    add_token_to_db(refresh_token, current_app.config['JWT_IDENTITY_CLAIM'])

    return jsonify(ret), 201
