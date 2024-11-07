from flask import Blueprint, jsonify, request
from app.services.role_service import (
    get_all_role_select,
    get_all_roles,
    get_role_by_id,
    create_role,
    update_role,
    delete_role,
    create_role_permission
)
from app.schemas.role_schema import RoleQuerySchema, RoleQuerySelectSchema,RoleSchema,PermissionListSchema
from app.utils.error.error_handlers import ResourceNotFound
from app.utils.error.error_responses import *
from app.utils.pagination.page_link import create_page_link
role_bp = Blueprint('role', __name__, url_prefix='/api')

role_schema = RoleSchema()
@role_bp.route('/roles', methods=['GET'])
def get_roles():
    try:
        schema = RoleQuerySchema()
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

        roles = get_all_roles(page_link)
        return roles
    except Exception as e:
        return server_error_message(details=str(e))

@role_bp.route('/role-select', methods=['GET'])
def get_role_select():
    try:
        schema = RoleQuerySelectSchema()
        try:
            params = schema.load(request.args)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        #get se params
        text_search = params.get('text_search', '')
        
        roles = get_all_role_select(text_search)
        return roles
    except Exception as e:
        return server_error_message(details=str(e))

@role_bp.route('/roles/<int:id>', methods=['GET'])
def get_role(id):
    try:
        role = get_role_by_id(id)
        return role
    except ResourceNotFound as e:
        return not_found_message(entity="Rol", details=str(e))
    except Exception as e:
        return server_error_message(details=str(e))

@role_bp.route('/roles', methods=['POST'])
def create_roles():
    try:
        try:
            req = role_schema.load(request.json)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        return create_role(req)
    except Exception as e:
        return server_error_message(details=str(e))

@role_bp.route('/roles/<int:id>', methods=['PUT'])
def update_role_route(id):
    try:

        try:
            req = role_schema.load(request.json, partial=True)
        except Exception as e:
            return bad_request_message(details=str(e))
    
        response = update_role(id, request.json)
        
        return response
    except Exception as e:
        return server_error_message(details=str(e))

@role_bp.route('/roles/<int:id>', methods=['DELETE'])
def delete_role_route(id):
    try:
        return delete_role(id)
    except Exception as e:
        return server_error_message(details=str(e))
    

@role_bp.route('/roles/<int:role_id>/update_permissions', methods=['POST'])
def assing_role_permissions(role_id):
    
    schema = PermissionListSchema()
    try:
        params = schema.load(request.json)
    except Exception as e:
        return bad_request_message(details=str(e))
        
    return create_role_permission(role_id,request.json)