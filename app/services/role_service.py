
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

        data = role_schema_many.dump(roles_paginated)
        
        return pagination_response(roles_paginated.total,roles_paginated.pages,roles_paginated.page,roles_paginated.per_page,data=data)
    except Exception as e:
        raise Exception(str(e))

def get_role_by_id(role_id):
    try:
        role = Role.query.get(role_id)
        if not role:
            raise ResourceNotFound("Role not found")
        return (role_schema.dump(role))
    except ResourceNotFound as e:
        raise ResourceNotFound("Role not found")
    
def create_role(data):
    try:
      
        db.session.add(data)
        db.session.commit()
        return created_ok_message(message="El Rol ha sido creado correctamente!")
    except Exception as err:
        db.session.rollback()
        return server_error_message(details=str(err))

def update_role(role_id, data):
    try:
        role = Role.query.get(role_id)
        if not role:
            raise ValueError("Role not found")
        role = role_schema.load(data, instance=role, partial=True)
        db.session.commit()
        return ok_message()
    except ValueError as err:
        raise ValueError("Role not found")
    except Exception as e:
        db.session.rollback()
        raise Exception(str(e)) 

def delete_role(role_id):
    try:
        role = Role.query.get(role_id)
        if not role:
            raise ValueError("Role not found")
        db.session.delete(role)
        db.session.commit()
        return True
    except ValueError as err:
        db.session.rollback()
        raise ValueError("Role not found")
    except Exception as e:
        db.session.rollback()
        raise Exception(str(e))

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
                raise ValueError("Role not found")
        
        role = Role.query.get(role_id)
        
        data = data.get('permissions', [])
        
        for item in data:
            if not get_permission_by_id(item):
                raise ValueError("Permission not found")
        
        role.permissions = Permission.query.filter(Permission.permission_id.in_(data)).all()
        
        db.session.commit()
        return created_ok_message(message="La asigancion se ha realizado correctamente!")
        
    except ValueError as e:
        return not_found_message(entity= "Rol o Permiso")
    except IntegrityError as ie:
        db.session.rollback()
        return conflict_message()
    except Exception as err:
        db.session.rollback()
        return controlled_error_message(details=str("Invalid operation"),message=str(err),code=404)