
from sqlalchemy import asc, desc, or_
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.schemas.role_permission_schema import RolePermissionSchema
from app.utils.success_responses import pagination_response,created_ok_message,ok_message
from app.utils.error.error_responses import  not_found_message,server_error_message,conflict_message,controlled_error_message
from app.services.role_service import get_role_by_id
from app.services.permission_service import get_permission_by_id
from sqlalchemy.exc import IntegrityError
from db import db


role_permission_schema = RolePermissionSchema()
role_permission_schema_many = RolePermissionSchema(many=True)

""" def get_all_role_permissions(pagelink):
    try:
        
        query = RolePermission.query

        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort_order)
        
        role_permissions_paginated = query.paginate(page=pagelink.page, per_page=pagelink.page_size, error_out=False)

        data = role_permission_schema_many.dump(role_permissions_paginated)
        
        return pagination_response(role_permissions_paginated.total,role_permissions_paginated.pages,role_permissions_paginated.page,role_permissions_paginated.per_page,data=data)
    except Exception as e:
        raise Exception(str(e)) """

def get_role_permission_by_id(role_permission_id):
    try:
        role_permission = RolePermission.query.get(role_permission_id)
        if not role_permission:
            raise ValueError("RolePermission not found")
        return (role_permission_schema.dump(role_permission))
    except ValueError as e:
        raise ValueError("RolePermission not found")
    


def update_role_permission(role_permission_id, data):
    try:
        role_permission = RolePermission.query.get(role_permission_id)
        if not role_permission:
            raise ValueError("RolePermission not found")
        role_permission = role_permission_schema.load(data, instance=role_permission, partial=True)
        db.session.commit()
        return ok_message()
    except ValueError as err:
        raise ValueError("RolePermission not found")
    except Exception as e:
        db.session.rollback()
        raise Exception(str(e)) 

def delete_role_permission(role_permission_id):
    try:
        role_permission = RolePermission.query.get(role_permission_id)
        if not role_permission:
            raise ValueError("RolePermission not found")
        db.session.delete(role_permission)
        db.session.commit()
        return True
    except ValueError as err:
        db.session.rollback()
        raise ValueError("RolePermission not found")
    except Exception as e:
        db.session.rollback()
        raise Exception(str(e))

def apply_filters_and_pagination(query, text_search=None, sort_order=None):
    
    

    if text_search:
       
        search_filter = or_(
            RolePermission.name.ilike(f'%{text_search}%'),
            RolePermission.description.ilike(f'%{text_search}%')
        )
        query = query.filter(search_filter)

    
    if sort_order.property_name:
        if sort_order.direction == 'ASC':
            query = query.order_by(asc(sort_order.property_name))
        else:
            query = query.order_by(desc(sort_order.property_name))

    return query
