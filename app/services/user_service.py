
from app.models.role import Role
from app.models.user import User
from app.schemas.user_schema import UserSchema, UserSchemaView
from app.services.role_service import get_role_by_id
from app.utils.error.error_handlers import ResourceNotFound,ValidationErrorExc
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

def get_users_service(pagelink):
    try:
        
        query = db.session.query(User.created_at, User.email, User.first_name, User.last_name, User.second_last_name, User.last_name, User.user_id,Role.description.label("role"), User.status).join(Role, User.role_id == Role.role_id)

        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort_order)
        
        users_paginated = query.paginate(page=pagelink.page, per_page=pagelink.page_size, error_out=False)
        if not users_paginated.items:
            return not_found_message(message="Parece que aun no hay datos")
        data = user_schema_many.dump(users_paginated)
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

def update_user(user_id, data):
    try:
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFound("User not found")
        
        # Realizar las validaciones comunes
        validate_user_data(data, user)

        
        # Actualizar el usuario
        user = user_schema.load(data, instance=user, partial=True)
        db.session.commit()

        return ok_message()
    except ValidationErrorExc as ve:
        db.session.rollback()
        return bad_request_message(message= str(ve),details=str(ve))
    except IntegrityError as ie:
        db.session.rollback()
        return conflict_message(details=ie)
    except ResourceNotFound as e:
        db.session.rollback()
        return not_found_message(details=e, entity="Rol O Usuario")

def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFound("Usuario not found")
        db.session.delete(user)
        db.session.commit()
        return '',204
    except ResourceNotFound as e:
        db.session.rollback()
        return not_found_message(details=e, entity="Usuario")

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

def apply_filters_and_pagination(query, text_search=None, sort_order=None):
    
    if text_search:
       
        search_filter = or_(
            User.first_name.ilike(f'%{text_search}%'),
            User.last_name.ilike(f'%{text_search}%'),
            User.email.ilike(f'%{text_search}%')
        )
        query = query.filter(search_filter)

    
    if sort_order.property_name:
        if sort_order.direction == 'ASC':
            query = query.order_by(asc(sort_order.property_name))
        else:
            query = query.order_by(desc(sort_order.property_name))
    
    return query

def validate_user_data(data, user=None):
    # Verificar si el correo ya existe
    if data.get("email"):
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and (user is None or existing_user.user_id != user.user_id):
            
            raise ValueError("El correo electrónico ya está registrado.")
    

    # Validar si el rol existe
    if data.get("role_id"):
        role_id = data.get("role_id")
        if role_id and not get_role_by_id(role_id):
            raise ResourceNotFound("Role not found")

    # Verificar la contraseña solo si se está actualizando o creando
    if data.get("password"):
        password = data.get("password")
        if password:
            check, message = check_password(password)
            if not check:
                raise ValidationErrorExc(str(message))

    return True