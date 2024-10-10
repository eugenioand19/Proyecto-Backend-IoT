from flask import Blueprint, jsonify, request
from app.services.wetland_service import (
    get_all_wetlands,
    get_wetland_by_id,
    create_wetland,
    update_wetland,
    delete_wetland
)
from app.schemas.wetland_schema import WetlandQuerySchema
from app.utils.error.error_responses import *
from app.utils.pagination.page_link import create_page_link
wetland_bp = Blueprint('wetland', __name__, url_prefix='/api')

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
        return jsonify(wetlands), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wetland_bp.route('/wetlands/<int:id>', methods=['GET'])
def get_wetland(id):
    try:
        wetland = get_wetland_by_id(id)
        return jsonify(wetland), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wetland_bp.route('/wetlands', methods=['POST'])
def create_wetlands():
    try:
        wetland = create_wetland(request.json)
        return jsonify(wetland), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400  # Error de validación
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wetland_bp.route('/wetlands/<int:id>', methods=['PUT'])
def update_wetland_route(id):
    try:
        wetland = update_wetland(id, request.json)
        return jsonify(wetland), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wetland_bp.route('/wetlands/<int:id>', methods=['DELETE'])
def delete_wetland_route(id):
    try:
        delete_wetland(id)
        return '', 204
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404  # Nodo no encontrado
    except Exception as e:
        return jsonify({'error': str(e)}), 500