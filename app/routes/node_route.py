from flask import Blueprint, jsonify, request
from app.services.node_service import (
    get_all_nodes,
    get_node_by_id,
    create_node,
    update_node,
    delete_node,
    assing_sensors_service
)
from marshmallow.exceptions import ValidationError
from app.schemas.node_schema import NodeQuerySchema,NodeSchema, SensorsListSchema
from app.utils.error.error_handlers import ResourceNotFound, ValidationErrorExc
from app.utils.error.error_responses import *
from app.utils.pagination.page_link import create_page_link
node_bp = Blueprint('node', __name__, url_prefix='/api')

node_schema = NodeSchema()
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
        sort_property = params.get('sort_property', 'created_at')
        sort_order = params.get('sort_order', 'ASC')
        statusList = params.get('statusList', '')
        typesList = params.get('typesList', '')
        
        #create de pagination object
        page_link = create_page_link(page_size,page,text_search,sort_property,sort_order)

        nodes = get_all_nodes(page_link,statusList=statusList,typesList=typesList)
        return nodes
    except Exception as e:
        return server_error_message(details=str(e))

@node_bp.route('/nodes/<int:id>', methods=['GET'])
def get_node(id):
    try:
        node = get_node_by_id(id)
        return node
    except ResourceNotFound as e:
        return not_found_message(entity="Alerta", details=str(e))
    except Exception as e:
        return server_error_message(details=str(e))

@node_bp.route('/nodes', methods=['POST'])
def create_nodes():
    try:
        try:
            req = node_schema.load(request.json)
        except ValidationError as e:
            return bad_request_message(details=str(e.messages)) 
        
        return create_node(req)
    except Exception as e:
        return server_error_message(details=str(e))

@node_bp.route('/nodes/<int:id>', methods=['PUT'])
def update_node_route(id):
    try:

        try:
            req = node_schema.load(request.json, partial=True)
        except ValidationError as e:
            return bad_request_message(details=str(e.messages))  
    
        response = update_node(id, request.json)
        
        return response
    except Exception as e:
        return server_error_message(details=str(e))

@node_bp.route('/nodes/<int:id>', methods=['DELETE'])
def delete_node_route(id):
    try:
        
        return delete_node(id)
    except Exception as e:
        return server_error_message(details=str(e))
    

@node_bp.route('/nodes/<int:node_id>/update_sensors', methods=['POST'])
def assing_sensors(node_id):
    
    schema = SensorsListSchema()
    try:
        params = schema.load(request.json)
    except Exception as e:
        return bad_request_message(details=str(e))
    
    return assing_sensors_service(node_id,request.json)
    