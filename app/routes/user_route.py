from flask import Blueprint, jsonify, request
from app.services.user_service import (
    get_users_service,
    get_user_by_id,
    create_user,
    update_user,
    delete_user
)
from app.schemas.user_schema import UserQuerySchema,UserSchema,UserSchemaView, UserUpdateSchema
from app.utils.error.error_responses import *
from app.utils.pagination.page_link import create_page_link
user_bp = Blueprint('user', __name__, url_prefix='/api')

user_schema = UserSchema()
user_up_schema = UserUpdateSchema()
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
        sort = params.get('sort', 'created_at.asc')

        #create de pagination object
        page_link = create_page_link(page_size, page, text_search, sort)
        
        #response ok
        return get_users_service(page_link, params=params)
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
        
    

@user_bp.route('/users', methods=['PUT'])
def update_user_route():
    try:

        try:
            req = user_up_schema.load(request.json, partial=True)
        except Exception as e:
            return bad_request_message(details=str(e))
    
        response = update_user(request.json)
        
        return response
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@user_bp.route('/users', methods=['DELETE'])
def delete_user_route():
    try:
        
        return delete_user(request.json)
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)