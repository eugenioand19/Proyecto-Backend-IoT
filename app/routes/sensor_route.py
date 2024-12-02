from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.decorators.user_role import role_required
from app.services.sensor_service import (
    get_all_sensor_select,
    get_all_sensors,
    get_sensor_by_id,
    create_sensor,
    update_sensor,
    delete_sensor,
    get_all_type_sensors
)
from app.schemas.sensor_schema import SensorQuerySchema, SensorQuerySelectSchema, SensorSchema, SensorsUpdateSchema
from app.utils.error.error_responses import *
from app.utils.pagination.page_link import create_page_link
from app.utils.success_responses import ok_message
from app.models.type_sensor import TypeSensor

sensor_bp = Blueprint('sensor', __name__, url_prefix='/api')

sensor_schema = SensorSchema()
sensor_upt_schema =SensorsUpdateSchema()

@sensor_bp.route('/sensors', methods=['GET'])
@jwt_required()
@role_required(['ADMIN'])
def get_sensors():
    try:
        schema = SensorQuerySchema()
        try:
            params = schema.load(request.args)
        except Exception as e:
            return bad_request_message(details=str(e))
        user_id = get_jwt_identity()
        page_size = params['page_size']
        page = params['page']
        text_search = params.get('text_search', '')
        sort = params.get('sort', 'created_at.asc')
        statusList = params.get('statusList', '')
        typesList = params.get('typesList', '')
        name = params.get('name', '')
        status = params.get('status', '')
        type_sensor = params.get('type_sensor', '')
        # Load allowed types dynamically
        """   allowed_types = [ type_sensor.name for type_sensor in TypeSensor.query.all()]
        if any(type_ not in allowed_types for type_ in typesList.split(',')) and typesList:
            return bad_request_message(details="Invalid type in typesList") """
        
        page_link = create_page_link(page_size, page, text_search, sort)

        sensors = get_all_sensors(page_link, params=params)

        return sensors
    except Exception as e:
        return server_error_message(details=str(e))

@sensor_bp.route('/sensors/<int:id>', methods=['GET'])
@jwt_required()
@role_required(['ADMIN'])
def get_sensor(id):
    try:
        user_id = get_jwt_identity()
        sensor = get_sensor_by_id(id)
        return ok_message(sensor)
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@sensor_bp.route('/sensors', methods=['POST'])
@jwt_required()
@role_required(['ADMIN'])
def create_sensors():
    try:
        user_id = get_jwt_identity()
        try:
            req = sensor_schema.load(request.json)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        return create_sensor(req)
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@sensor_bp.route('/sensors', methods=['PUT'])
@jwt_required()
@role_required(['ADMIN'])
def update_sensor_route():
    try:
        user_id = get_jwt_identity()
        try:
            
            req = sensor_upt_schema.load(request.json, partial=True)
        except Exception as e:
            
            return bad_request_message(details=str(e))
        
        response = update_sensor(request.json)
        
        return response
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@sensor_bp.route('/sensors', methods=['DELETE'])
@jwt_required()
@role_required(['ADMIN'])
def delete_sensor_route():
    try:
        user_id = get_jwt_identity()
        return delete_sensor(request.json)
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@sensor_bp.route('/sensors/type_sensors', methods=['GET'])
@jwt_required()
@role_required(['ADMIN'])
def get_all_typesensors():
    try:
        user_id = get_jwt_identity()
        return get_all_type_sensors()
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@sensor_bp.route('/sensor-select', methods=['GET'])
@sensor_bp.route('/sensor-select/<int:node_id>', methods=['GET'])
@jwt_required()

def get_sensor_select(node_id=None):

    try:
        
        schema = SensorQuerySelectSchema()
        try:
            params = schema.load(request.args)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        text_search = params.get('text_search', '')
        
        sensors = get_all_sensor_select(text_search, node_id)
        return sensors
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)