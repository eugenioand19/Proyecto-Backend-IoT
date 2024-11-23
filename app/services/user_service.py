
import uuid
from app.models.role import Role
from app.models.user import User
from app.models.user_wetland import UserWetland
from app.models.wetland import Wetland
from app.schemas.user_schema import UserSchema, UserSchemaView
from app.services.role_service import get_role_by_id
from app.services.wetland_service import get_wetland_by_id
from app.utils.error.error_handlers import ResourceNotFound,ValidationErrorExc
from app.utils.pagination.filters import apply_filters_and_pagination
from db import db
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_,asc, desc
import re
from app.utils.error.error_responses import *
from app.utils.success_responses import created_ok_message,pagination_response,ok_message

user_schema = UserSchema()
user_schema_many = UserSchemaView(many=True)
user_schema_view = UserSchemaView()

def get_users_service(pagelink,params=None):
    try:
        
        query = db.session.query(User.created_at, User.email, User.first_name, User.last_name, User.second_name, User.second_last_name, User.last_name, User.user_id,Role.description.label("role_desc"), Role.role_id.label("role_id"), User.status,Role.name.label("role_code")).join(Role, User.role_id == Role.role_id)

        
        
        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort_order, params=params, entities=[User,Role])
        
        users_paginated = query.paginate(page=pagelink.page, per_page=pagelink.page_size, error_out=False)
        if not users_paginated.items:
            return not_found_message(message="Parece que aun no hay datos")
        
        data=[]

        for row in users_paginated:
            
            obj={
                "first_name": row.first_name,
                "created_at": row.created_at,
                "last_name": row.last_name,
                "role": {
                    "description": row.role_desc,
                    "code": row.role_code,
                    "role_id": row.role_id
                },
                "second_name": row.second_name,
                "second_last_name": row.second_last_name,
                "status" : row.status,
                "email": row.email,
                "user_id": row.user_id
            }

            data.append(obj)
        return pagination_response(users_paginated.total,users_paginated.pages,users_paginated.page,users_paginated.per_page,data=data)
    except Exception as e:
        print(e)
        raise Exception("Error al obtener los usuarios") from e

def get_user_by_id(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        return user_schema_view.dump(user)
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception("Error al obtener el usuario") from e

def create_user(data):
    try:
        

        validate_user_data(data)
        
        first_name = data.get("first_name")
        second_name = data.get("second_name","")
        last_name = data.get("last_name")
        second_last_name = data.get("second_last_name","")
        email = data.get("email")
        password = data.get("password")
        role_id = data.get("role_id")

        user = User(
            first_name = first_name,
            second_name = second_name,
            last_name = last_name,
            second_last_name = second_last_name,
            email = email,
            role_id = role_id
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return created_ok_message(message="El usuario fue creado exitosamente.")
    except ValidationErrorExc as ve:
        db.session.rollback()
        return bad_request_message(details=str(ve))
    except ValueError as va:
        return conflict_message(details=va)
    except IntegrityError as ie:
        db.session.rollback()
        return conflict_message(details=ie) 
    except ResourceNotFound as e:
        db.session.rollback()
        return not_found_message(details=e,entity="Rol") 

def update_user(data):
    try:
        
        updated_users = []
        # Verificar si se envió la lista de humedales
        if not isinstance(data.get("users"), list):
            return bad_request_message(details="El formato de los datos es incorrecto. Se esperaba una lista de Usuarios.")
        for user_data in data["users"]:
            user_id = user_data.get("user_id")
            if not user_id:
                return bad_request_message(details="Falta el campo 'user_id' en uno de los Usuarios.")

            # Obtener el user de la base de datos
            user = User.query.get(user_id)
            if not user:
                return not_found_message(entity="User", message=f"User con ID {user_id} no encontrado.")
            validate =  validate_user_data(user_data,user)
            # Actualizar el user
            
            user = user_schema.load(user_data, instance=user, partial=True)
            
            
            updated_users.append(user)

        # Confirmar los cambios en la base de datos
        db.session.commit()
        
        return ok_message(message=f"{len(updated_users)} Usuarios actualizados exitosamente.")
    except ResourceNotFound as err:
        return not_found_message(entity="User", details=str(err),)
    except ValidationErrorExc as val:
        return bad_request_message(message=str(val))


def delete_user(data):
    try:
        # Validar que la lista de usuarios esté presente en la petición
        user_ids = data.get("users")
        if not user_ids or not isinstance(user_ids, list):
            return bad_request_message(details="El campo 'users' debe ser una lista de IDs de usuarios.")

        # Convertir los IDs de usuario a UUID
        try:
            user_ids = [uuid.UUID(uid) for uid in user_ids]
        except ValidationErrorExc as e:

            return bad_request_message(details="Uno o más IDs no son válidos UUID.")

        # Consultar los usuarios que existen en la base de datos
        users = User.query.filter(User.user_id.in_(user_ids)).all()

        # Identificar los usuarios no encontrados
        found_ids = {user.user_id for user in users}
        missing_ids = set(user_ids) - found_ids

        if missing_ids:
            return not_found_message(details=f"Usuarios no encontrados: {list(map(str, missing_ids))}", entity="User")

        # Eliminar los usuarios encontrados
        for user in users:
            db.session.delete(user)

        # Confirmar los cambios
        db.session.commit()

        return ok_message(message=f"{len(users)} usuarios eliminados exitosamente.")
    except ValidationErrorExc as val:
        print("fff")
        return bad_request_message(message=str(val))
    except Exception as e:
        db.session.rollback()
        return server_error_message(details=str(e))

def check_password(password):
    # Password requirements
    min_length = 8
    has_upper = re.search(r'[A-Z]', password) is not None
    has_lower = re.search(r'[a-z]', password) is not None
    has_digit = re.search(r'\d', password) is not None
    has_special = re.search(r'[@$!%*?&]', password) is not None

    # Check for length requirements
    if len(password) < min_length:
        return False, "La contraseña debe tener al menos 8 digitos"
    # Check for uppercase letter
    if not has_upper:
        return False, "La contraseña debe contener al menos 1 mayuscula"
    # Check for lowercase letter
    if not has_lower:
        return False, "La contraseña debe contener al menos 1 minuscula"
    # Check for digit
    if not has_digit:
        return False, "La contraseña debe contener al menos 1 digito"
    # Check for special character
    if not has_special:
        return False, "La contraseña debe contener al menos 1 caracter especial(@, $, !, %, *, ?, &)."

    return True, "Password is secure."



def validate_user_data(data, user=None):
    # Verificar si el correo ya existe
    if data.get("email"):
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and (user is None or existing_user.user_id != user.user_id):
            
            raise ValidationErrorExc("Uno de los correos que intenta actualizar ya está registrado.")
    

    # Validar si el rol existe
    if data.get("role_id"):
        role_id = data.get("role_id")
        if role_id and not get_role_by_id(role_id):
            raise ResourceNotFound("Rol no encontrado")

    # Verificar la contraseña solo si se está actualizando o creando
    if data.get("password"):
        password = data.get("password")
        if password:
            check, message = check_password(password)
            if not check:
                raise ValidationErrorExc(str(message))

    return True

""" def assing_wetlands_service(user_id, data):
    try:
        user = User.query.get(user_id)

        if user is None:
            raise ResourceNotFound("El Usuario no ha sido encontrado")
        
        # Obtener los wetlandes del JSON enviado
        new_wetland_ids = data.get('wetlands', [])

        # Validar que todos los wetlandes existen
        existing_wetlands = Wetland.query.filter(Wetland.wetland_id.in_(new_wetland_ids)).all()
        existing_wetland_ids = {wetland.wetland_id for wetland in existing_wetlands}
        missing_wetland_ids = set(new_wetland_ids) - existing_wetland_ids

        if missing_wetland_ids:
            raise ResourceNotFound(f"Los siguientes wetlandes no existen: {missing_wetland_ids}")
        
        
        
        # Verificar los wetlandes ya existentes en el nodo
        existing_wetland_users = UserWetland.query.filter_by(user_id=user_id).all()
        existing_wetland_ids = [wetland_user.wetland_id for wetland_user in existing_wetland_users]
        
        # Actualizar los wetlandes existentes y marcar los no presentes como INACTIVO
        for wetland_user in existing_wetland_users:
            if wetland_user.wetland_id in new_wetland_ids:
                wetland_user.status = "ACTIVE"  # Cambiar el estado a ACTIVO
                wetland_user.installation_date = db.func.current_timestamp()  # Actualizar fecha de instalación
                wetland_user.removal_date = None  # Restablecer la fecha de remoción
            else:
                wetland_user.status = "INACTIVE"  # Cambiar el estado a INACTIVO
                wetland_user.removal_date = db.func.current_timestamp()  # Actualizar fecha de remoción
        
        # Crear nuevos registros para los wetlandes que no están asignados aún
        for wetland_id in new_wetland_ids:
            if wetland_id not in existing_wetland_ids:
                new_wetland_user = UserWetland(
                    user_id=user_id,
                    wetland_id=wetland_id,
                    status="ACTIVE",
                    installation_date=db.func.current_timestamp()
                )
                db.session.add(new_wetland_user)
        
        # Guardar los cambios
        db.session.commit()
        return created_ok_message(message="La asigancion se ha realizado correctamente!")
    except ResourceNotFound as nf:
        db.session.rollback()
        return not_found_message(details=str(nf))
    except ValidationErrorExc as ve:
        db.session.rollback()
        return bad_request_message(message= str(ve),details=str(ve))
    except Exception as err:
        db.session.rollback()
        error_message = ' '.join(str(err).split()[:5])
        return server_error_message(details=error_message)
     """

def assing_wetlands_service(user_id,data):
    try:

        if not get_user_by_id(user_id):
                raise ResourceNotFound("Role not found")
        
        user = User.query.get(user_id)
        
        data = data.get('wetlands', [])
        
        for item in data:
            if not get_wetland_by_id(item):
                raise ResourceNotFound("Humedal not found")
        
        user.wetlands = Wetland.query.filter(Wetland.wetland_id.in_(data)).all()
        
        db.session.commit()
        return created_ok_message(message="La asigancion se ha realizado correctamente!")
        
    except ResourceNotFound as e:
        return not_found_message(entity= "Rol o Permiso")
    except IntegrityError as ie:
        db.session.rollback()
        return conflict_message()
    except Exception as err:
        db.session.rollback()
        return controlled_error_message(details=str("Invalid operation"),message=str(err),code=404)