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
from app.schemas.sensor_schema import SensorQuerySchema, SensorQuerySelectSchema,SensorSchema
from app.utils.error.error_responses import *
from app.utils.pagination.page_link import create_page_link
sensor_bp = Blueprint('sensor', __name__, url_prefix='/api')

sensor_schema = SensorSchema()
@sensor_bp.route('/sensors', methods=['GET'])
def get_sensors():

    try:
        schema = SensorQuerySchema()
        try:
            params = schema.load(request.args)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        #get se params
        page_size = params['page_size']
        page = params['page']
        text_search = params.get('text_search', '')
        sort_property = params.get('sort_property', 'created_at')
        sort_order = params.get('sort_order', 'ASC')
        statusList = params.get('statusList', '')
        typesList = params.get('typesList', '')
        
        #create de pagination object
        page_link = create_page_link(page_size,page,text_search,sort_property,sort_order)

        sensors = get_all_sensors(page_link,statusList=statusList,typesList=typesList)

        return sensors
    except Exception as e:
        return server_error_message(details=str(e))

@sensor_bp.route('/sensors/<int:id>', methods=['GET'])
def get_sensor(id):
    try:
        sensor = get_sensor_by_id(id)
        return sensor
    except Exception as e:
        return server_error_message(details=str(e))

@sensor_bp.route('/sensors', methods=['POST'])
def create_sensors():
    try:
        try:
            req = sensor_schema.load(request.json)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        return create_sensor(req)
    except Exception as e:
        return server_error_message(details=str(e))

@sensor_bp.route('/sensors/<int:id>', methods=['PUT'])
def update_sensor_route(id):
    try:

        try:
            req = sensor_schema.load(request.json, partial=True)
        except Exception as e:
            return bad_request_message(details=str(e))
    
        response = update_sensor(id, request.json)
        
        return response
    except Exception as e:
        return server_error_message(details=str(e))

@sensor_bp.route('/sensors/<int:id>', methods=['DELETE'])
def delete_sensor_route(id):
    try:
        
        return delete_sensor(id)
    except Exception as e:
        return server_error_message(details=str(e))

@sensor_bp.route('/sensors/type_sensors', methods=['GET'])
def get_all_typesensors():

    try:
        return get_all_type_sensors()
    except Exception as e:
        return server_error_message(details=str(e))

@sensor_bp.route('/sensor-select', methods=['GET'])
def get_sensor_select():
    try:
        schema = SensorQuerySelectSchema()
        try:
            params = schema.load(request.args)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        #get se params
        text_search = params.get('text_search', '')
        
        sensors = get_all_sensor_select(text_search)
        return sensors
    except Exception as e:
        return server_error_message(details=str(e))