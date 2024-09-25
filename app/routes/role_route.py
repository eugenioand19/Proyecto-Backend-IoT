from flask import Blueprint, jsonify, request
from app.services.role_service import (
    get_all_roles,
    get_role_by_id,
    create_role,
    update_role,
    delete_role
)

role_bp = Blueprint('role', __name__, url_prefix='/api')

@role_bp.route('/roles', methods=['GET'])
def get_roles():
    try:
        roles = get_all_roles()
        return jsonify(roles), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@role_bp.route('/roles/<int:id>', methods=['GET'])
def get_role(id):
    try:
        role = get_role_by_id(id)
        return jsonify(role), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@role_bp.route('/roles', methods=['POST'])
def create_roles():
    try:
        role = create_role(request.json)
        return jsonify(role), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400  # Error de validación
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@role_bp.route('/roles/<int:id>', methods=['PUT'])
def update_role_route(id):
    try:
        role = update_role(id, request.json)
        return jsonify(role), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@role_bp.route('/roles/<int:id>', methods=['DELETE'])
def delete_role_route(id):
    try:
        delete_role(id)
        return '', 204
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500