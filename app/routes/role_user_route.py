from flask import Blueprint, jsonify, request
from app.services.role_user_service import (
    get_all_role_users,
    get_role_user_by_id,
    create_role_user,
    update_role_user,
    delete_role_user
)

role_user_bp = Blueprint('role_user', __name__, url_prefix='/api')

@role_user_bp.route('/role_users', methods=['GET'])
def get_role_users():
    try:
        role_users = get_all_role_users()
        return jsonify(role_users), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@role_user_bp.route('/role_users/<int:id>', methods=['GET'])
def get_role_user(id):
    try:
        role_user = get_role_user_by_id(id)
        return jsonify(role_user), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@role_user_bp.route('/role_users', methods=['POST'])
def create_role_users():
    try:
        role_user = create_role_user(request.json)
        return jsonify(role_user), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400  # Error de validación
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@role_user_bp.route('/role_users/<int:id>', methods=['PUT'])
def update_role_user_route(id):
    try:
        role_user = update_role_user(id, request.json)
        return jsonify(role_user), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@role_user_bp.route('/role_users/<int:id>', methods=['DELETE'])
def delete_role_user_route(id):
    try:
        delete_role_user(id)
        return '', 204
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500