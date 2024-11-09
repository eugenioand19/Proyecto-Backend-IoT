
from sqlite3 import IntegrityError
from sqlalchemy import asc, desc, or_
from app.models.permission import Permission
from app.models.role import Role
from app.schemas.role_schema import RoleSchema
from app.services.permission_service import get_permission_by_id
from app.utils.error.error_handlers import ResourceNotFound
from app.utils.success_responses import pagination_response,created_ok_message,ok_message
from app.utils.error.error_responses import bad_request_message, conflict_message, controlled_error_message, not_found_message,server_error_message
from db import db


role_schema = RoleSchema()
role_schema_many = RoleSchema(many=True)

def get_all_roles(pagelink):
    try:
        
        query = Role.query

        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort_order)
        
        roles_paginated = query.paginate(page=pagelink.page, per_page=pagelink.page_size, error_out=False)
        if not roles_paginated.items:
            return not_found_message(message="Parece que aun no hay datos")
        data = role_schema_many.dump(roles_paginated)
        
        return pagination_response(roles_paginated.total,roles_paginated.pages,roles_paginated.page,roles_paginated.per_page,data=data)
    except Exception as e:
        raise Exception(str(e))

def get_role_by_id(role_id):
    role = Role.query.get(role_id)
    if not role:
        raise ResourceNotFound("Rol no encontrado")
    return role_schema.dump(role)
    
def create_role(data):
    try:

        # Validar si el rol ya existe
        if Role.query.filter_by(name=data.name).first():
            return conflict_message(details="Ya existe un rol con ese nombre.")
    
        db.session.add(data)
        db.session.commit()
        return created_ok_message(message="El Rol ha sido creado correctamente!")
    except Exception as err:
        db.session.rollback()
        return server_error_message(details=str(err))

def get_all_role_select(text_search):
    try:
        
        query = Role.query
        if text_search:
       
            search_filter = or_(
                Role.name.ilike(f'%{text_search}%'),
                Role.description.ilike(f'%{text_search}%')
            )
            query = query.filter(search_filter)
        
        query = query.with_entities(Role.role_id, Role.name,Role.description).all()
        if not query:
            return not_found_message(message="Parece que aun no hay datos")
        data = role_schema_many.dump(query)
        
        return ok_message(data=data)
    except Exception as e:
        raise Exception(str(e))

def update_role(role_id, data):
    try:

        role = Role.query.get(role_id)

        if not role:
            raise ResourceNotFound("Rol no encontrado")
        
        # Validar si el rol ya existe
        if Role.query.filter_by(name=data.get("name")).first():
            return conflict_message(details="Ya existe un rol con ese nombre.")
        
        role = role_schema.load(data, instance=role, partial=True)
        db.session.commit()
        return ok_message()
    except ResourceNotFound as e:
        db.session.rollback()
        return not_found_message(details=e,entity="Rol")


def delete_role(role_id):
    try:
        role = Role.query.get(role_id)
        if not role:
            raise ResourceNotFound("Rol no encontrado")
        
        db.session.delete(role)
        db.session.commit()
        return '',204
    except ResourceNotFound as e:
        return not_found_message(details=str(e),entity="Rol")

def apply_filters_and_pagination(query, text_search=None, sort_order=None):
    
    if text_search:
        search_filter = or_(
            Role.name.ilike(f'%{text_search}%'),
            Role.description.ilike(f'%{text_search}%')
        )
        query = query.filter(search_filter)

    
    if sort_order.property_name:
        if sort_order.direction == 'ASC':
            query = query.order_by(asc(sort_order.property_name))
        else:
            query = query.order_by(desc(sort_order.property_name))

    return query

def create_role_permission(role_id,data):
    try:

        if not get_role_by_id(role_id):
                raise ResourceNotFound("Role not found")
        
        role = Role.query.get(role_id)
        
        data = data.get('permissions', [])
        
        for item in data:
            if not get_permission_by_id(item):
                raise ResourceNotFound("Permission not found")
        
        role.permissions = Permission.query.filter(Permission.permission_id.in_(data)).all()
        
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