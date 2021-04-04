from app.models import User


def query_existing_user(user_id):
    user = User.query.filter(User.deleted == False).filter((User.id == user_id))
    return user

