
from app.models.user import User
from app.schemas.user_schema import UserSchema
from db import db
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

user_schema = UserSchema()
user_schema_many = UserSchema(many=True)

def get_all_users():
    try:
        users = User.query.all()
        return user_schema_many.dump(users)
    except Exception as e:
        # Manejo de errores a nivel de servicio
        raise Exception("Error al obtener los nodos de sensores") from e

def get_user_by_id(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        return user_schema.dump(user)
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception("Error al obtener el nodo de sensor") from e

def create_user(data):
    try:
        user_data = user_schema.load(data)  # Aquí se lanzará un ValidationError si falla

        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            raise ValueError("El correo electrónico ya está registrado.")
        
        name = data.get("name")
        last_name = data.get("last_name")
        email = data.get("email")
        password = data.get("password")

        user = User(
            name = name,
            last_name = last_name,
            email = email
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user_schema.dump(user)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except IntegrityError as ie:
        db.session.rollback()
        raise ValueError("Error de integridad, posible duplicado") from ie
    except ValueError as ve:
        db.session.rollback() 
        return {"error": str(ve)}, 400 
    except Exception as e:
        print(e)
        db.session.rollback()  # Asegúrate de revertir cambios en caso de error
        raise Exception("Error al crear el usuario") from e

def update_user(user_id, data):
    try:
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        user = user_schema.load(data, instance=user, partial=True)
        db.session.commit()
        return user_schema.dump(user)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al actualizar el nodo de sensor") from e

def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        db.session.delete(user)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al eliminar el nodo de sensor") from e
