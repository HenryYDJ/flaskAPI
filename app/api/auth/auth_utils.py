from datetime import datetime, timezone

from sqlalchemy.orm.exc import NoResultFound
from flask_jwt_extended import decode_token

from app.models import TokenBlacklist
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
        jti = jti,
        token_type = token_type,
        user_id = user_id,
        expires = expires,
        revoked = revoked
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
        tokens = TokenBlacklist.query.filter(TokenBlacklist.user_id==user_id, TokenBlacklist.revoked==False).all()
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