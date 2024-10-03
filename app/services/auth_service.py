from flask_jwt_extended import create_access_token, create_refresh_token
from app.models.user import User

def authenticate_user(data):
    user = User.query.filter_by(email=data.get("email")).first()
    if user and user.check_password(data.get("password")):
        return user
    return None

def create_tokens(user):
    
    access_token = create_access_token(identity=user.user_id)
    refresh_token = create_refresh_token(identity=user.user_id)
    return access_token, refresh_token