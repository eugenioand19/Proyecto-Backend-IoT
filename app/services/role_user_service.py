
from app.models.role_user import RoleUser
from app.schemas.role_user_schema import RoleuserSchema
from db import db
from marshmallow import ValidationError

role_user_schema = RoleuserSchema()
role_user_schema_many = RoleuserSchema(many=True)

def get_all_role_users():
    try:
        role_users = RoleUser.query.all()
        return role_user_schema_many.dump(role_users)
    except Exception as e:
        # Manejo de errores a nivel de servicio
        raise Exception("Error al obtener los nodos de sensores") from e

def get_role_user_by_id(role_user_id):
    try:
        role_user = RoleUser.query.get(role_user_id)
        if not role_user:
            raise ValueError("Roleuser not found")
        return role_user_schema.dump(role_user)
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception("Error al obtener el nodo de sensor") from e

def create_role_user(data):
    try:
        role_user = role_user_schema.load(data)  # Aquí se lanzará un ValidationError si falla
        db.session.add(role_user)
        db.session.commit()
        return role_user_schema.dump(role_user)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except Exception as e:
        db.session.rollback()  # Asegúrate de revertir cambios en caso de error
        raise Exception("Error al crear el nodo de sensor") from e

def update_role_user(role_user_id, data):
    try:
        role_user = RoleUser.query.get(role_user_id)
        if not role_user:
            raise ValueError("Roleuser not found")
        role_user = role_user_schema.load(data, instance=role_user, partial=True)
        db.session.commit()
        return role_user_schema.dump(role_user)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al actualizar el nodo de sensor") from e

def delete_role_user(role_user_id):
    try:
        role_user = RoleUser.query.get(role_user_id)
        if not role_user:
            raise ValueError("Roleuser not found")
        db.session.delete(role_user)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al eliminar el nodo de sensor") from e
