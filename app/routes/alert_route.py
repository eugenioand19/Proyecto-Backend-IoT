from flask import Blueprint, jsonify, request
from app.services.alert_service import (
    get_all_alerts,
    get_alert_by_id,
    create_alert,
    update_alert,
    delete_alert
)

alert_bp = Blueprint('alert', __name__, url_prefix='/api')

@alert_bp.route('/alerts', methods=['GET'])
def get_alerts():
    try:
        alerts = get_all_alerts()
        return jsonify(alerts), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/alerts/<int:id>', methods=['GET'])
def get_alert(id):
    try:
        alert = get_alert_by_id(id)
        return jsonify(alert), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/alerts', methods=['POST'])
def create_alerts():
    try:
        alert = create_alert(request.json)
        return jsonify(alert), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400  # Error de validación
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/alerts/<int:id>', methods=['PUT'])
def update_alert_route(id):
    try:
        alert = update_alert(id, request.json)
        return jsonify(alert), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/alerts/<int:id>', methods=['DELETE'])
def delete_alert_route(id):
    try:
        delete_alert(id)
        return '', 204
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  
    except Exception as e:
        return jsonify({'error': str(e)}), 500