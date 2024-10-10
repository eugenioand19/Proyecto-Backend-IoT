from flask import Blueprint, jsonify, request
from app.schemas.user_schema import UserQuerySchema
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.utils.error.error_responses import bad_request_message,server_error_message
from app.utils.pagination.page_link import create_page_link
from app.services.user_service import (
    get_users_service,
    get_user_by_id,
    create_user,
    update_user,
    delete_user
)

user_bp = Blueprint('user', __name__, url_prefix='/api')


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

        #create de pagination object
        page_link = create_page_link(page_size,page,text_search,sort_property,sort_order)
        
        #response ok
        return get_users_service(page_link)
    except Exception as e:
        return server_error_message(details=str(e))

@user_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    try:
        user = get_user_by_id(id)
        return jsonify(user), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users', methods=['POST'])
def create_users():
    try:
        user, status_code = create_user(request.json)
        return jsonify(user), status_code
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400  # Error de validación
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:id>', methods=['PUT'])
def update_user_route(id):
    try:
        user = update_user(id, request.json)
        return jsonify(user), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user_route(id):
    try:
        delete_user(id)
        return '', 204
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500