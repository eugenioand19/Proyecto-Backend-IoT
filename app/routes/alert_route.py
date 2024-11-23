from flask import Blueprint, jsonify, request
from app.services.alert_service import (
    get_all_alerts,
    get_alert_by_id,
    create_alert,
    update_alert,
    delete_alert
)
from app.schemas.alert_schema import AlertQuerySchema,AlertSchema, AlertsUpdateSchema
from app.utils.error.error_handlers import ResourceNotFound
from app.utils.error.error_responses import *
from app.utils.pagination.page_link import create_page_link, create_time_page_link
from app.utils.success_responses import ok_message
alert_bp = Blueprint('alert', __name__, url_prefix='/api')

alert_schema = AlertSchema()
alert_schema_upt = AlertsUpdateSchema()
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
        sort = params.get('sort', 'created_at.asc')
        
        #create de pagination object
        page_link = create_page_link(page_size, page, text_search, sort)

        alerts = get_all_alerts(page_link,params=params)

        return alerts
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@alert_bp.route('/alerts/<int:id>', methods=['GET'])
def get_alert(id):
    try:
        alert = get_alert_by_id(id)
        return ok_message(alert)
    except ResourceNotFound as e:
        return not_found_message(entity="Alerta", details=str(e))
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

""" @alert_bp.route('/alerts', methods=['POST'])
def create_alerts():
    try:
        try:
            req = alert_schema.load(request.json)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        return create_alert(req)
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message) """

@alert_bp.route('/alerts', methods=['PUT'])
def update_alert_route():
    try:

        try:
            req = alert_schema_upt.load(request.json, partial=True)
        except Exception as e:
            return bad_request_message(details=str(e))
    
        response = update_alert(request.json)
        
        return response
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@alert_bp.route('/alerts', methods=['DELETE'])
def delete_alert_route():
    try:
        return delete_alert(request.json)
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)