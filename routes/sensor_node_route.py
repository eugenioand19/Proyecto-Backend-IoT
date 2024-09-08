from flask import Blueprint, jsonify, request
from models.sensor_node import SensorNode
from schemas.sensor_node_schema import SensorNodeSchema
from db import db
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
sensor_node_bp = Blueprint('sensor_node', __name__)

#endpoint to get all sensor nodes
@sensor_node_bp.route('/sensor_nodes', methods=['GET'])
def get_sensor_nodes():
    sensor_nodes = SensorNode.query.all()
    sensor_node_schema = SensorNodeSchema(many=True)
    return jsonify(sensor_node_schema.dump(sensor_nodes))

#endpoint to get a sensor node by id
@sensor_node_bp.route('/sensor_nodes/<int:id>', methods=['GET'])
def get_sensor_node(id):
    try:
        sensor_node = SensorNode.query.get(id)
        if sensor_node:
            sensor_node_schema = SensorNodeSchema()
            return jsonify(sensor_node_schema.dump(sensor_node))
        return jsonify({"error": "Sensor node not found"}), 404
    except SQLAlchemyError as e:
        print(e)
        return jsonify({"error": "An error occurred while retrieving the sensor node"}), 500

#endpoint to create a new sensor node
@sensor_node_bp.route('/sensor_nodes', methods=['POST'])
def create_sensor_nodes():
    sensor_node_schema = SensorNodeSchema()
    try:
        sensor_node = sensor_node_schema.load(request.json)
        db.session.add(sensor_node)
        db.session.commit()
        return jsonify(sensor_node_schema.dump(sensor_node)), 201
    
    except ValidationError as err:
        return jsonify(err.messages), 400
    except SQLAlchemyError as e:
        db.session.rollback() 
        return jsonify({"error": "An Error ocurred while saving the sensor node on the database" }), 500
    
#endpoint to update a sensor node
@sensor_node_bp.route('/sensor_nodes/<int:id>', methods=['PUT'])
def update_sensor_node(id):
    sensor_node = SensorNode.query.get(id)
    if sensor_node:
        sensor_node_schema = SensorNodeSchema()
        try:
            sensor_node = sensor_node_schema.load(request.json, instance=sensor_node, partial=True)
            db.session.commit()
            return jsonify(sensor_node_schema.dump(sensor_node)), 200
        except ValidationError as err:
            return jsonify(err.messages), 400
        except SQLAlchemyError as e:
            print(e)
            db.session.rollback() 
            return jsonify({"error": "An Error occurred while updating the sensor node in the database"}), 500
    return jsonify({"error": "Sensor node not found"}), 404

#endpoint to delete a sensor node
@sensor_node_bp.route('/sensor_nodes/<int:id>', methods=['DELETE'])
def delete_sensor_node(id):
    try:
        sensor_node = SensorNode.query.get(id)
        if sensor_node:
            db.session.delete(sensor_node)
            db.session.commit()
            return jsonify({"message": "Sensor node deleted successfully"}), 204
        return jsonify({"error": "Sensor node not found"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the sensor node"}), 500
