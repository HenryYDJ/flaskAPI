from datetime import datetime, timezone
from functools import wraps

from flask import jsonify
from sqlalchemy.orm.exc import NoResultFound
from flask_jwt_extended import decode_token, verify_jwt_in_request, get_jwt_identity, get_jwt_claims

from app.models import TokenBlacklist, User, Teacher

from app import db

from .exceptions import TokenNotFound


def posix_utc_to_datetime(posix_utc):
    return datetime.fromtimestamp(posix_utc, tz=timezone.utc)


def add_token_to_db(encoded_token, identity_claim):
    decoded_token = decode_token(encoded_token)

    jti = decoded_token['jti']
    token_type = decoded_token['type']
    user_id = decoded_token[identity_claim].get('id')
    expires = posix_utc_to_datetime(decoded_token['exp'])
    revoked = False

    db_token = TokenBlacklist(
        jti=jti,
        token_type=token_type,
        user_id=user_id,
        expires=expires,
        revoked=revoked
    )
    db.session.add(db_token)
    db.session.commit()


def is_token_revoked(decoded_token):
    """
    Since we add every token to the db, so if a token is not found in the db, it is considered revoked.
    """
    jti = decoded_token['jti']
    try:
        token = TokenBlacklist.query.filter_by(jti=jti).one()
        return token.revoked
    except NoResultFound:
        return True


def revoke_token(jti):
    try:
        token = TokenBlacklist.query.filter_by(jti=jti).one()
        token.revoked = True
        db.session.commit()
    except NoResultFound:
        raise TokenNotFound("Could not find the token")


def get_user_tokens(user_id):
    """
    Returns all of the tokens, revoked and unrevoked, that are stored for the
    given user
    """
    try:
        tokens = TokenBlacklist.query.filter_by(user_id=user_id).all()
        return tokens
    except NoResultFound:
        raise TokenNotFound("No token for this user")


def get_user_unrevoked_tokens(user_id):
    """
    Returns all of the unrevoked tokens that belong to given user.
    """
    try:
        tokens = TokenBlacklist.query.filter(TokenBlacklist.user_id == user_id, TokenBlacklist.revoked == False).all()
        return tokens
    except NoResultFound:
        raise TokenNotFound("No token for this user")


def logout_user(user_id):
    active_tokens = get_user_unrevoked_tokens(user_id)
    if active_tokens:
        for token in active_tokens:
            token.revoked = True
        db.session.commit()


def prune_db():
    """
    Delete all tokens that have expired
    """
    now = datetime.utcnow()
    expired_tokens = TokenBlacklist.query.filter(TokenBlacklist.expires < now).all()
    for token in expired_tokens:
        db.session.delete(token)

    db.session.commit()


def jwt_roles_required(roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            client = get_jwt_claims().get('client')
            user_id = get_jwt_identity().get('id')
            # First need to get the user based on the client
            if client == 0:
                user = Teacher.query.filter(Teacher.deleted == False).filter(Teacher.id == user_id).first()
            elif client == 1:
                user = User.query.filter(User.deleted == False).filter(User.openID == user_id).first()
            else:
                return jsonify(msg='wrong client'), 401

            # Check if the user is qualified for the action or resources
            if user:
                user_roles = user.get_roles()
                if user_roles >= roles:
                    return fn(*args, **kwargs)
                else:
                    return jsonify(msg='not qualified'), 403
            else:
                return jsonify(msg='no such user'), 400

        return decorator
    return wrapper




