from flask import Blueprint, jsonify, request
from app.services.data_history_service import (
    get_all_data_historys,
    get_data_history_by_id,
    create_data_history,
    update_data_history,
    delete_data_history
)
from app.utils.error.error_responses import server_error_message

data_history_bp = Blueprint('data_history', __name__, url_prefix='/api')

@data_history_bp.route('/data_historys', methods=['GET'])
def get_data_historys():
    try:
        data_historys = get_all_data_historys()
        return jsonify(data_historys), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_history_bp.route('/data_historys/<int:id>', methods=['GET'])
def get_data_history(id):
    try:
        data_history = get_data_history_by_id(id)
        return jsonify(data_history), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_history_bp.route('/data_historys', methods=['POST'])
def create_data_historys():
    try:
        data_history = create_data_history(request.json)
        return jsonify(data_history), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400  # Error de validación
    except Exception as e:
        #error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=e)

@data_history_bp.route('/data_historys/<int:id>', methods=['PUT'])
def update_data_history_route(id):
    try:
        data_history = update_data_history(id, request.json)
        return jsonify(data_history), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_history_bp.route('/data_historys/<int:id>', methods=['DELETE'])
def delete_data_history_route(id):
    try:
        delete_data_history(id)
        return '', 204
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500