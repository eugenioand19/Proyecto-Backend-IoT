from flask import Blueprint, jsonify, request
from app.services.wetland_service import (
    get_all_wetlands,
    get_wetland_by_id,
    create_wetland,
    update_wetland,
    delete_wetland
)

wetland_bp = Blueprint('wetland', __name__, url_prefix='/api')

@wetland_bp.route('/wetlands', methods=['GET'])
def get_wetlands():
    try:
        wetlands = get_all_wetlands()
        return jsonify(wetlands), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wetland_bp.route('/wetlands/<int:id>', methods=['GET'])
def get_wetland(id):
    try:
        wetland = get_wetland_by_id(id)
        return jsonify(wetland), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wetland_bp.route('/wetlands', methods=['POST'])
def create_wetlands():
    try:
        wetland = create_wetland(request.json)
        return jsonify(wetland), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400  # Error de validación
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wetland_bp.route('/wetlands/<int:id>', methods=['PUT'])
def update_wetland_route(id):
    try:
        wetland = update_wetland(id, request.json)
        return jsonify(wetland), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wetland_bp.route('/wetlands/<int:id>', methods=['DELETE'])
def delete_wetland_route(id):
    try:
        delete_wetland(id)
        return '', 204
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500