from flask import Blueprint, jsonify, request
from app.services.alert_service import (
    get_all_alerts,
    get_alert_by_id,
    create_alert,
    update_alert,
    delete_alert
)
from app.schemas.alert_schema import AlertQuerySchema,AlertSchema
from app.utils.error.error_responses import *
from app.utils.pagination.page_link import create_time_page_link
alert_bp = Blueprint('alert', __name__, url_prefix='/api')

alert_schema = AlertSchema()
@alert_bp.route('/alerts', methods=['GET'])
def get_alerts():
    try:
        schema = AlertQuerySchema()
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
        severityList = params.get('severityList', '')
        starTime = params.get('starTime', '')
        endTime = params.get('endTime', '')
        
        #create de pagination object
        page_link = create_time_page_link(page_size,page,text_search,sort_property,sort_order,starTime,endTime)

        alerts = get_all_alerts(page_link,statusList=statusList,severityList=severityList)

        return alerts
    except Exception as e:
         return server_error_message(details=str(e))

@alert_bp.route('/alerts/<int:id>', methods=['GET'])
def get_alert(id):
    try:
        alert = get_alert_by_id(id)
        return alert
    except ValueError as ve:
        return not_found_message(details=str(ve))
    except Exception as e:
        return server_error_message(details=str(e))

@alert_bp.route('/alerts', methods=['POST'])
def create_alerts():
    try:
        try:
            req = alert_schema.load(request.json)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        return create_alert(req)
    except Exception as e:
        print("jshfsf")
        return server_error_message(details=str(e))

@alert_bp.route('/alerts/<int:id>', methods=['PUT'])
def update_alert_route(id):
    try:

        try:
            req = alert_schema.load(request.json, partial=True)
        except Exception as e:
            return bad_request_message(details=str(e))
    
        response = update_alert(id, request.json)
        
        return response
    except ValueError as e:
        return not_found_message(details=e)
    except Exception as e:
        return server_error_message(details=str(e))

@alert_bp.route('/alerts/<int:id>', methods=['DELETE'])
def delete_alert_route(id):
    try:
        delete_alert(id)
        return '', 204
    except ValueError as ve:
        return not_found_message(details=ve)
    except Exception as e:
        return server_error_message(details=str(e))