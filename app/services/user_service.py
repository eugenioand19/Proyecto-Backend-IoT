
from app.models.user import User
from app.schemas.user_schema import UserSchema
from db import db
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_,asc, desc
import re
from app.utils.error.error_responses import *
from app.utils.success_responses import created_ok_message,pagination_response

user_schema = UserSchema()
user_schema_many = UserSchema(many=True)

def get_users_service(pagelink):
    try:
        
        query = User.query

        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort_order)
        
        users_paginated = query.paginate(page=pagelink.page, per_page=pagelink.page_size, error_out=False)

        data = user_schema_many.dump(users_paginated)
        
        return pagination_response(users_paginated.total,users_paginated.pages,users_paginated.page,users_paginated.per_page,data=data)
    except Exception as e:
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

        """ existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            raise ValueError("El correo electrónico ya está registrado.") """
        
        name = data.get("name")
        last_name = data.get("last_name")
        email = data.get("email")
        password = data.get("password")

        check, message = check_password(password)

        if check:
            pass
        else:
            raise ValueError(message)

        user = User(
            name = name,
            last_name = last_name,
            email = email
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return created_ok_message(message="El usuario fue creado exitosamente.")
    except ValidationError as ve:
        db.session.rollback()
        return bad_request_message()
    except IntegrityError as ie:
        db.session.rollback()
        return conflict_message() 
    
    except ValueError as ie:
        db.session.rollback()
        return { 
                    "data": [{ "errors":[ 
                { 
                    "code":400,
                    "message": "",
                }
            ]}],
            "message": str(ie)
           
        },400
    except Exception as e:
        db.session.rollback()
        return {
            "message": "An unexpected error occurred. Please try again later.",
            "technical_message": str(e)  # General error message
        }, 500

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
            User.name.ilike(f'%{text_search}%'),
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