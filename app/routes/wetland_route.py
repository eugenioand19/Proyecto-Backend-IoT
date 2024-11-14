from flask import Blueprint, jsonify, request
from app.schemas.reports_schema import ReportQuerySchema
from app.services.wetland_service import (
    get_all_wetland_select,
    get_all_wetlands,
    get_wetland_by_id,
    create_wetland,
    get_wetlands_overview,
    get_wetlands_overview_details,
    update_wetland,
    delete_wetland,
    wetlands_reports
)
from app.schemas.wetland_schema import WetlandQuerySchema, WetlandQuerySelectSchema,WetlandSchema
from app.utils.error.error_handlers import ResourceNotFound
from app.utils.error.error_responses import *
from app.utils.pagination.page_link import create_page_link, create_time_page_link
from app.utils.success_responses import ok_message
wetland_bp = Blueprint('wetland', __name__, url_prefix='/api')

wetland_schema = WetlandSchema()
@wetland_bp.route('/wetlands', methods=['GET'])
def get_wetlands():
    try:
        schema = WetlandQuerySchema()
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

        
        #create de pagination object
        page_link = create_page_link(page_size,page,text_search,sort_property,sort_order)

        wetlands = get_all_wetlands(page_link,statusList=statusList)
        return wetlands
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@wetland_bp.route('/wetland-select', methods=['GET'])
def get_wetland_select():
    try:
        schema = WetlandQuerySelectSchema()
        try:
            params = schema.load(request.args)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        #get se params
        text_search = params.get('text_search', '')
        
        wetlands = get_all_wetland_select(text_search)
        return wetlands
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)
    
@wetland_bp.route('/wetlands/<int:id>', methods=['GET'])
def get_wetland(id):
    try:
        wetland = get_wetland_by_id(id)
        return ok_message(wetland)
    except ResourceNotFound as e:
        return not_found_message(entity="Humedal", details=str(e))
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@wetland_bp.route('/wetlands', methods=['POST'])
def create_wetlands():
    try:
        try:
            req = wetland_schema.load(request.json)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        return create_wetland(req)
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@wetland_bp.route('/wetlands/<int:id>', methods=['PUT'])
def update_wetland_route(id):
    try:

        try:
            req = wetland_schema.load(request.json, partial=True)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        response = update_wetland(id, request.json)
        
        return response
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@wetland_bp.route('/wetlands/<int:id>', methods=['DELETE'])
def delete_wetland_route(id):
    try:
        
        return delete_wetland(id)

    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@wetland_bp.route('/wetlands-overview', methods=['GET'])
def get_wetlands_dashboard():

    try:
        
        return get_wetlands_overview()
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)


@wetland_bp.route('/wetlands-overview/<int:id_wetland>', methods=['GET'])
def get_wetlands_dashboard_details(id_wetland):

    try:
        
        return get_wetlands_overview_details(id_wetland)
    except Exception as err:
        return server_error_message(details=str(err))
@wetland_bp.route('/wetland-report', methods=['GET'])
@wetland_bp.route('/wetland-report/<int:wetland_id>', methods=['GET'])
@wetland_bp.route('/wetland-report/<int:wetland_id>/<int:node_id>', methods=['GET'])
@wetland_bp.route('/wetland-report/<int:wetland_id>/<int:node_id>/<int:sensor_id>', methods=['GET'])
def get_reports_wetland(wetland_id = None, node_id= None, sensor_id = None):
    try:
        schema = ReportQuerySchema()
        try:
            params = schema.load(request.args)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        #get se params
        page_size = params['page_size']
        page = params['page']
        sort_property = params.get('sort_property', 'created_at')
        sort_order = params.get('sort_order', 'ASC')
        start_time = params.get('start_time', '')
        end_time = params.get('end_time', '')
        sensor_type = params.get('sensor_type', '')
        #create de pagination object
        page_link = create_time_page_link(page_size,page,'',sort_property,sort_order,start_time,end_time)

        report = wetlands_reports(wetland_id=wetland_id, node_id=node_id, sensor_id=sensor_id,pagelink=page_link,type_sensor=sensor_type)

        return report
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)