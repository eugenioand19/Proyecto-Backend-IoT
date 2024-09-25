
from app.models.role import Role
from app.schemas.role_schema import RoleSchema
from db import db
from marshmallow import ValidationError

role_schema = RoleSchema()
role_schema_many = RoleSchema(many=True)

def get_all_roles():
    try:
        roles = Role.query.all()
        return role_schema_many.dump(roles)
    except Exception as e:
        # Manejo de errores a nivel de servicio
        raise Exception("Error al obtener los nodos de sensores") from e

def get_role_by_id(role_id):
    try:
        role = Role.query.get(role_id)
        if not role:
            raise ValueError("Role not found")
        return role_schema.dump(role)
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception("Error al obtener el nodo de sensor") from e

def create_role(data):
    try:
        role = role_schema.load(data)  # Aquí se lanzará un ValidationError si falla
        db.session.add(role)
        db.session.commit()
        return role_schema.dump(role)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except Exception as e:
        db.session.rollback()  # Asegúrate de revertir cambios en caso de error
        raise Exception("Error al crear el nodo de sensor") from e

def update_role(role_id, data):
    try:
        role = Role.query.get(role_id)
        if not role:
            raise ValueError("Role not found")
        role = role_schema.load(data, instance=role, partial=True)
        db.session.commit()
        return role_schema.dump(role)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al actualizar el nodo de sensor") from e

def delete_role(role_id):
    try:
        role = Role.query.get(role_id)
        if not role:
            raise ValueError("Role not found")
        db.session.delete(role)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al eliminar el nodo de sensor") from e
