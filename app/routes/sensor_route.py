from flask import Blueprint, jsonify, request
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
def get_sensors():
    try:
        schema = SensorQuerySchema()
        try:
            params = schema.load(request.args)
        except Exception as e:
            return bad_request_message(details=str(e))
        
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
def get_sensor(id):
    try:
        sensor = get_sensor_by_id(id)
        return ok_message(sensor)
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@sensor_bp.route('/sensors', methods=['POST'])
def create_sensors():
    try:
        try:
            req = sensor_schema.load(request.json)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        return create_sensor(req)
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@sensor_bp.route('/sensors', methods=['PUT'])
def update_sensor_route():
    try:
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
def delete_sensor_route():
    try:
        return delete_sensor(request.json)
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@sensor_bp.route('/sensors/type_sensors', methods=['GET'])
def get_all_typesensors():
    try:
        return get_all_type_sensors()
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@sensor_bp.route('/sensor-select', methods=['GET'])
@sensor_bp.route('/sensor-select/<int:node_id>', methods=['GET'])
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