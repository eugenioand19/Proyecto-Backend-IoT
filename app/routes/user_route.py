from flask import Blueprint, jsonify, request
from app.services.user_service import (
    get_users_service,
    get_user_by_id,
    create_user,
    update_user,
    delete_user
)
from app.schemas.user_schema import UserQuerySchema,UserSchema,UserSchemaView
from app.utils.error.error_responses import *
from app.utils.pagination.page_link import create_page_link
user_bp = Blueprint('user', __name__, url_prefix='/api')

user_schema = UserSchema()
@user_bp.route('/users', methods=['GET'])
def get_users():
    try:
        
        schema = UserQuerySchema()

        #Validate req params
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
        statusList = params.get('statusList', '')
        roleList = params.get('roleList', '')

        #create de pagination object
        page_link = create_page_link(page_size,page,text_search,sort_property,sort_order)
        
        #response ok
        return get_users_service(page_link,statusList=statusList, RoleList=roleList)
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)
    
@user_bp.route('/users/<uuid:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = get_user_by_id(user_id)
        return user
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@user_bp.route('/users', methods=['POST'])
def create_users():
    try:
        try:
            req = user_schema.load(request.json)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        return create_user(request.json)
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)
        
    

@user_bp.route('/users/<uuid:user_id>', methods=['PUT'])
def update_user_route(user_id):
    try:

        try:
            req = user_schema.load(request.json, partial=True)
        except Exception as e:
            return bad_request_message(details=str(e))
    
        response = update_user(user_id, request.json)
        
        return response
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@user_bp.route('/users/<uuid:user_id>', methods=['DELETE'])
def delete_user_route(user_id):
    try:
        
        return delete_user(user_id)
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)