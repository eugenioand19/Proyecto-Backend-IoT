from flask import Blueprint, jsonify, request
from app.services.sensor_service import (
    get_all_sensors,
    get_sensor_by_id,
    create_sensor,
    update_sensor,
    delete_sensor
)

sensor_bp = Blueprint('sensor', __name__, url_prefix='/api')

@sensor_bp.route('/sensors', methods=['GET'])
def get_sensors():
    try:
        sensors = get_all_sensors()
        return jsonify(sensors), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sensor_bp.route('/sensors/<int:id>', methods=['GET'])
def get_sensor(id):
    try:
        sensor = get_sensor_by_id(id)
        return jsonify(sensor), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sensor_bp.route('/sensors', methods=['POST'])
def create_sensors():
    try:
        sensor = create_sensor(request.json)
        return jsonify(sensor), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400  # Error de validación
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sensor_bp.route('/sensors/<int:id>', methods=['PUT'])
def update_sensor_route(id):
    try:
        sensor = update_sensor(id, request.json)
        return jsonify(sensor), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sensor_bp.route('/sensors/<int:id>', methods=['DELETE'])
def delete_sensor_route(id):
    try:
        delete_sensor(id)
        return '', 204
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500