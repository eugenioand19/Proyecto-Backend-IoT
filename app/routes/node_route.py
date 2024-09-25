from flask import Blueprint, jsonify, request
from app.services.node_service import (
    get_all_nodes,
    get_node_by_id,
    create_node,
    update_node,
    delete_node
)

node_bp = Blueprint('node', __name__, url_prefix='/api')

@node_bp.route('/nodes', methods=['GET'])
def get_nodes():
    try:
        nodes = get_all_nodes()
        return jsonify(nodes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@node_bp.route('/nodes/<int:id>', methods=['GET'])
def get_node(id):
    try:
        node = get_node_by_id(id)
        return jsonify(node), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@node_bp.route('/nodes', methods=['POST'])
def create_nodes():
    try:
        node = create_node(request.json)
        return jsonify(node), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400  # Error de validación
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@node_bp.route('/nodes/<int:id>', methods=['PUT'])
def update_node_route(id):
    try:
        node = update_node(id, request.json)
        return jsonify(node), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@node_bp.route('/nodes/<int:id>', methods=['DELETE'])
def delete_node_route(id):
    try:
        delete_node(id)
        return '', 204
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500