
from sqlalchemy import asc, desc, or_
from app.models.permission import Permission
from app.schemas.permission_schema import PermissionSchema
from app.utils.error.error_handlers import ResourceNotFound
from app.utils.success_responses import pagination_response,created_ok_message,ok_message
from app.utils.error.error_responses import bad_request_message, conflict_message, not_found_message,server_error_message, unauthorized_message
from db import db


permission_schema = PermissionSchema()
permission_schema_many = PermissionSchema(many=True)

def get_all_permissions(pagelink):
    try:
        
        query = Permission.query

        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort_order)
        
        permissions_paginated = query.paginate(page=pagelink.page, per_page=pagelink.page_size, error_out=False)
        if not permissions_paginated.items:
            return not_found_message(message="Parece que aun no hay datos")
        data = permission_schema_many.dump(permissions_paginated)
        
        return pagination_response(permissions_paginated.total,permissions_paginated.pages,permissions_paginated.page,permissions_paginated.per_page,data=data)
    except Exception as e:
        raise Exception(str(e))

def get_all_permissions_select(text_search):
    try:
        
        query = Permission.query
        if text_search:
       
            search_filter = or_(
                Permission.name.ilike(f'%{text_search}%'),
                Permission.description.ilike(f'%{text_search}%')
            )
            query = query.filter(search_filter)
        
        query = query.with_entities(Permission.permission_id, Permission.name, Permission.description).all()
        if not query:
            return not_found_message(message="Parece que aun no hay datos")
        data = permission_schema_many.dump(query)
        
        return ok_message(data=data)
    except Exception as e:
        raise Exception(str(e))

def get_permission_by_id(permission_id):
    try:
        permission = Permission.query.get(permission_id)
        if not permission:
            raise ValueError("Permission not found")
        return (permission_schema.dump(permission))
    except ValueError as e:
        raise ValueError("Permission not found")
    
def get_permission_by_id(permission_id):
    permission = Permission.query.get(permission_id)
    if not permission:
        raise ResourceNotFound("Permiso no encontrado")
    return permission_schema.dump(permission)
    
def create_permission(data):
    try:
        if Permission.query.filter_by(code=data.code).first():
            return conflict_message(details="Ya existe un Permiso con ese Codigo.")
        db.session.add(data)
        db.session.commit()
        return created_ok_message(message="El Permiso ha sido creado correctamente!")
    except Exception as err:
        db.session.rollback()
        return server_error_message(details=str(err))

def update_permission(permission_id, data):
    try:

        permission = Permission.query.get(permission_id)

        if not permission:
            raise ResourceNotFound("Permiso no encontrado")
        
        if data.get("code"):
            return unauthorized_message(details="Acceso no Autotizado")
        
        permission = permission_schema.load(data, instance=permission, partial=True)
        db.session.commit()
        return ok_message()
    except ResourceNotFound as e:
        db.session.rollback()
        return not_found_message(details=e,entity="Permiso")


def delete_permission(permission_id):
    try:
        permission = Permission.query.get(permission_id)
        if not permission:
            raise ResourceNotFound("Permiso no encontrado")
        
        db.session.delete(permission)
        db.session.commit()
        return '',204
    except ResourceNotFound as e:
        return not_found_message(details=str(e),entity="Permiso")

def apply_filters_and_pagination(query, text_search=None, sort_order=None):
    
    

    if text_search:
       
        search_filter = or_(
            Permission.name.ilike(f'%{text_search}%'),
            Permission.description.ilike(f'%{text_search}%')
        )
        query = query.filter(search_filter)

    
    if sort_order.property_name:
        if sort_order.direction == 'ASC':
            query = query.order_by(asc(sort_order.property_name))
        else:
            query = query.order_by(desc(sort_order.property_name))

    return query
