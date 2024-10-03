from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services.user_service import (
    get_all_users,
    get_user_by_id,
    create_user,
    update_user,
    delete_user
)

user_bp = Blueprint('user', __name__, url_prefix='/api')


@user_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        current_user = get_jwt_identity()  # Obtiene el usuario del token
        print(current_user)
        users = get_all_users()

        return jsonify(users), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        user = create_user(request.json)
        return jsonify(user), 201
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