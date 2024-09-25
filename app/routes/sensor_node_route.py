from flask import Blueprint, jsonify, request
from app.services.sensor_node_service import (
    get_all_sensor_nodes,
    get_sensor_node_by_id,
    create_sensor_node,
    update_sensor_node,
    delete_sensor_node
)

sensor_node_bp = Blueprint('sensor_node', __name__, url_prefix='/api')

@sensor_node_bp.route('/sensor_nodes', methods=['GET'])
def get_sensor_nodes():
    try:
        sensor_nodes = get_all_sensor_nodes()
        return jsonify(sensor_nodes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sensor_node_bp.route('/sensor_nodes/<int:id>', methods=['GET'])
def get_sensor_node(id):
    try:
        sensor_node = get_sensor_node_by_id(id)
        return jsonify(sensor_node), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sensor_node_bp.route('/sensor_nodes', methods=['POST'])
def create_sensor_nodes():
    try:
        sensor_node = create_sensor_node(request.json)
        return jsonify(sensor_node), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400  # Error de validación
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sensor_node_bp.route('/sensor_nodes/<int:id>', methods=['PUT'])
def update_sensor_node_route(id):
    try:
        sensor_node = update_sensor_node(id, request.json)
        return jsonify(sensor_node), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sensor_node_bp.route('/sensor_nodes/<int:id>', methods=['DELETE'])
def delete_sensor_node_route(id):
    try:
        delete_sensor_node(id)
        return '', 204
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500