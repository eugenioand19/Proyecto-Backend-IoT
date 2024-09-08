from flask import Blueprint, jsonify, request
from models.node import Node
from schemas.node_schema import NodeSchema
from db import db
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
node_bp = Blueprint('node', __name__)

# endpoint to get all nodes
@node_bp.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = Node.query.all()
    node_schema = NodeSchema(many=True)
    return jsonify(node_schema.dump(nodes))

# endpoint to get a node by id
@node_bp.route('/nodes/<int:id>', methods=['GET'])
def get_node(id):
    try:
        node = Node.query.get(id)
        if node:
            node_schema = NodeSchema()
            return jsonify(node_schema.dump(node))
        return jsonify({"error": "Node not found"}), 404
    except SQLAlchemyError as e:
        print(e)
        return jsonify({"error": "An error occurred while retrieving the node"}), 500

# endpoint to create a new node
@node_bp.route('/nodes', methods=['POST'])
def create_node():
    node_schema = NodeSchema()
    try:
        node = node_schema.load(request.json)
        db.session.add(node)
        db.session.commit()
        return jsonify(node_schema.dump(node)), 201
    
    except ValidationError as err:
        return jsonify(err.messages), 400
    except SQLAlchemyError as e:
        db.session.rollback() 
        return jsonify({"error": "An Error ocurred while saving the node on the database" }), 500
    
# endpoint to update a node
@node_bp.route('/nodes/<int:id>', methods=['PUT'])
def update_node(id):
    node = Node.query.get(id)
    if node:
        node_schema = NodeSchema()
        try:
            node = node_schema.load(request.json, instance=node, partial=True)
            db.session.commit()
            return jsonify(node_schema.dump(node)), 200
        except ValidationError as err:
            return jsonify(err.messages), 400
        except SQLAlchemyError as e:
            print(e)
            db.session.rollback() 
            return jsonify({"error": "An Error occurred while updating the node in the database"}), 500
    return jsonify({"error": "Node not found"}), 404

# endpoint to delete a node
@node_bp.route('/nodes/<int:id>', methods=['DELETE'])
def delete_node(id):
    try:
        node = Node.query.get(id)
        if node:
            db.session.delete(node)
            db.session.commit()
            return jsonify({"message": "Node deleted successfully"}), 204
        return jsonify({"error": "Node not found"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the node"}), 500
