from flask import Blueprint, jsonify, request
from app.services.permission_service import (
    get_all_permissions,
    get_permission_by_id,
    create_permission,
    update_permission,
    delete_permission,
    get_all_permissions_select
)
from app.schemas.permission_schema import PermissionQuerySchema,PermissionSchema,PermissionQuerySelectSchema
from app.utils.error.error_responses import *
from app.utils.pagination.page_link import create_page_link
permission_bp = Blueprint('permission', __name__, url_prefix='/api')

permission_schema = PermissionSchema()
@permission_bp.route('/permissions', methods=['GET'])
def get_permissions():
    try:
        schema = PermissionQuerySchema()
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

        permissions = get_all_permissions(page_link)
        return permissions
    except Exception as e:
        return server_error_message(details=str(e))

@permission_bp.route('/permissions-select', methods=['GET'])
def get_permissions_select():
    try:
        schema = PermissionQuerySelectSchema()
        try:
            params = schema.load(request.args)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        #get se params
        text_search = params.get('text_search', '')

        
        #create de pagination object
        

        permissions = get_all_permissions_select(text_search)
        return permissions
    except Exception as e:
        return server_error_message(details=str(e))

@permission_bp.route('/permissions/<int:id>', methods=['GET'])
def get_permission(id):
    try:
        permission = get_permission_by_id(id)
        return permission
    except Exception as e:
        return server_error_message(details=str(e))

@permission_bp.route('/permissions', methods=['POST'])
def create_permissions():
    try:
        try:
            req = permission_schema.load(request.json)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        return create_permission(req)
    except Exception as e:
        return server_error_message(details=str(e))

@permission_bp.route('/permissions/<int:id>', methods=['PUT'])
def update_permission_route(id):
    try:

        try:
            req = permission_schema.load(request.json, partial=True)
        except Exception as e:
            return bad_request_message(details=str(e))
    
        response = update_permission(id, request.json)
        
        return response
    except Exception as e:
        return server_error_message(details=str(e))

@permission_bp.route('/permissions/<int:id>', methods=['DELETE'])
def delete_permission_route(id):
    try:
        return delete_permission(id)
    except Exception as e:
        return server_error_message(details=str(e))