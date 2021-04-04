from app.models import User


def query_existing_user(user_id):
    user = User.query.filter(User.deleted == False).filter((User.id == user_id)).first()
    return user


def query_validated_user(user_id):
    exist_user = query_existing_user(user_id)
    if exist_user.validated:
        return exist_user
    else:
        return None


def query_existing_phone_user(phone_number):
    user = User.query.filter(User.deleted == False).filter((User.phone == phone_number)).first()
    return user
