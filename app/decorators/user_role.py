from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User 
from app.models.role import Role 
from app.utils.error.error_responses import forbidden_message, server_error_message
from db import db
def role_required(required_roles):
    """
    Decorador para validar que el usuario tenga uno de los roles requeridos.
    :param required_roles: Lista de roles permitidos (e.g., ['ADMIN']).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Obtener el usuario autenticado
                user_id = get_jwt_identity()

                user_role = (
                    db.session.query(Role.code.label('role'))
                    .join(User, User.role_id == Role.role_id)
                    .filter(User.user_id == user_id)
                    .first()
                )
                
                if not user_role or user_role[0] not in required_roles:
                    return forbidden_message()
                
                return func(*args, **kwargs)
            except Exception as e:
                return server_error_message(details=str(e))
        return wrapper
    return decorator