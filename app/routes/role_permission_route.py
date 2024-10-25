from flask import Blueprint, jsonify, request
from app.services.role_permission_service import (
    get_role_permission_by_id,
    
    update_role_permission,
    delete_role_permission
)
from app.schemas.role_permission_schema import RolePermissionSchema,InputRolePermissionSchema
from app.utils.error.error_responses import *
from app.utils.pagination.page_link import create_page_link
role_permission_bp = Blueprint('role_permission', __name__, url_prefix='/api')

role_permission_schema = RolePermissionSchema()
input_role_permission_schema = InputRolePermissionSchema()
""" @role_permission_bp.route('/role_permissions', methods=['GET'])
def get_role_permissions():
    try:
        schema = RolePermissionQuerySchema()
        try:
            params = schema.load(request.args)
        except Exception as e:
            return bad_request_message(details=str(e))
        
         #get se params
        page_size = params['page_size']
        page = params['page']
        text_search = params.get('text_search', '')
        sort_property = params.get('sort_property', 'created_at')
        sort_order = params.get('sort_order', 'ASC')

        
        #create de pagination object
        page_link = create_page_link(page_size,page,text_search,sort_property,sort_order)

        role_permissions = get_all_role_permissions(page_link)
        return role_permissions
    except Exception as e:
         return server_error_message(details=str(e)) """


@role_permission_bp.route('/role_permissions/<int:id>', methods=['GET'])
def get_role_permission(id):
    try:
        role_permission = get_role_permission_by_id(id)
        return role_permission
    except ValueError as ve:
        return not_found_message(details=str(ve))
    except Exception as e:
        return server_error_message(details=str(e))



@role_permission_bp.route('/role_permissions/<int:id>', methods=['PUT'])
def update_role_permission_route(id):
    try:

        try:
            req = role_permission_schema.load(request.json, partial=True)
        except Exception as e:
            return bad_request_message(details=str(e))
    
        response = update_role_permission(id, request.json)
        
        return response
    except ValueError as e:
        return not_found_message(details=e)
    except Exception as e:
        return server_error_message(details=str(e))

@role_permission_bp.route('/role_permissions/<int:id>', methods=['DELETE'])
def delete_role_permission_route(id):
    try:
        delete_role_permission(id)
        return '', 204
    except ValueError as ve:
        return not_found_message(details=ve)
    except Exception as e:
        return server_error_message(details=str(e))