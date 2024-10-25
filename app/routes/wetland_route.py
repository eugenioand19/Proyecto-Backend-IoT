from flask import Blueprint, jsonify, request
from app.services.wetland_service import (
    get_all_wetlands,
    get_wetland_by_id,
    create_wetland,
    update_wetland,
    delete_wetland
)
from app.schemas.wetland_schema import WetlandQuerySchema,WetlandSchema
from app.utils.error.error_responses import *
from app.utils.pagination.page_link import create_page_link
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
         return server_error_message(details=str(e))

@wetland_bp.route('/wetlands/<int:id>', methods=['GET'])
def get_wetland(id):
    try:
        wetland = get_wetland_by_id(id)
        return wetland
    except Exception as e:
        return server_error_message(details=str(e))

@wetland_bp.route('/wetlands', methods=['POST'])
def create_wetlands():
    try:
        try:
            req = wetland_schema.load(request.json)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        return create_wetland(req)
    except Exception as e:
        return server_error_message(details=str(e))

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
        return server_error_message(details=str(e))

@wetland_bp.route('/wetlands/<int:id>', methods=['DELETE'])
def delete_wetland_route(id):
    try:
        
        return delete_wetland(id)

    except Exception as e:
        return server_error_message(details=str(e))