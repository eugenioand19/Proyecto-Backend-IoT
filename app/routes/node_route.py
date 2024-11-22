from flask import Blueprint, jsonify, request
from app.services.node_service import (
    get_all_node_select,
    get_all_nodes,
    get_node_by_id,
    create_node,
    update_node,
    delete_node,
    assing_sensors_service
)
from marshmallow.exceptions import ValidationError
from app.schemas.node_schema import NodeQuerySchema, NodeQuerySelectSchema,NodeSchema, NodeUpdateSchema, SensorsListSchema
from app.utils.error.error_handlers import ResourceNotFound, ValidationErrorExc
from app.utils.error.error_responses import *
from app.utils.pagination.page_link import create_page_link
from app.utils.success_responses import ok_message
node_bp = Blueprint('node', __name__, url_prefix='/api')

node_schema = NodeSchema()
node_schema_upt = NodeUpdateSchema()
@node_bp.route('/nodes', methods=['GET'])
def get_nodes():
    try:
        schema = NodeQuerySchema()
        try:
            params = schema.load(request.args)
        except ValidationError as e:
            return bad_request_message(details=str(e.messages))  

        params = schema.load(request.args)
        #get se params
        page_size = params['page_size']
        page = params['page']
        text_search = params.get('text_search', '')
        sort = params.get('sort', 'created_at.asc')

        
        #create de pagination object
        page_link = create_page_link(page_size, page, text_search, sort)

        nodes = get_all_nodes(page_link, params=params)
        return nodes
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@node_bp.route('/node-select', methods=['GET'])
@node_bp.route('/node-select/<int:wetland_id>', methods=['GET'])
def get_node_select(wetland_id=None):
    try:
        schema = NodeQuerySelectSchema()
        try:
            params = schema.load(request.args)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        #get se params
        text_search = params.get('text_search', '')
        
        nodes = get_all_node_select(text_search,wetland_id)
        return nodes
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@node_bp.route('/nodes/<int:id>', methods=['GET'])
def get_node(id):
    try:
        node = get_node_by_id(id)
        return ok_message(node)
    except ResourceNotFound as e:
        return not_found_message(entity="Nodo", details=str(e))
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@node_bp.route('/nodes', methods=['POST'])
def create_nodes():
    try:
        try:
            req = node_schema.load(request.json)
        except ValidationError as e:
            return bad_request_message(details=str(e.messages)) 
        
        return create_node(req)
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@node_bp.route('/nodes', methods=['PUT'])
def update_node_route():
    try:

        try:
            req = node_schema_upt.load(request.json, partial=True)
        except Exception as e:
            return bad_request_message(details=str(e))
        
        response = update_node(request.json)
        
        return response
    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)

@node_bp.route('/nodes', methods=['DELETE'])
def delete_node_route():
    try:
        
        return delete_node(request.json)

    except Exception as e:
        error_message = ' '.join(str(e).split()[:5])
        return server_error_message(details=error_message)
    

@node_bp.route('/nodes/<int:node_id>/update_sensors', methods=['POST'])
def assing_sensors(node_id):
    
    schema = SensorsListSchema()
    try:
        params = schema.load(request.json)
    except Exception as e:
        return bad_request_message(details=str(e))
    
    return assing_sensors_service(node_id,request.json)
    