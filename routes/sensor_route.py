from flask import Blueprint, jsonify, request
from models.sensor import Sensor
from schemas.sensor_schema import SensorSchema
from db import db
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
sensor_bp = Blueprint('sensor', __name__)

#endpoint to get all sensors
@sensor_bp.route('/sensors', methods=['GET'])
def get_sensors():
    sensors = Sensor.query.all()
    sensor_schema = SensorSchema(many=True)
    return jsonify(sensor_schema.dump(sensors))

#endpoint to get a sensor by id
@sensor_bp.route('/sensors/<int:id>', methods=['GET'])
def get_sensor(id):
    try:
        sensor = Sensor.query.get(id)
        if sensor:
            sensor_schema = SensorSchema()
            return jsonify(sensor_schema.dump(sensor))
        return jsonify({"error": "Sensor not found"}), 404
    except SQLAlchemyError as e:
        print(e)
        return jsonify({"error": "An error occurred while retrieving the sensor"}), 500

#endpoint to create a new sensor
@sensor_bp.route('/sensors', methods=['POST'])
def create_sensor():
    sensor_schema = SensorSchema()
    try:
        sensor = sensor_schema.load(request.json)
        db.session.add(sensor)
        db.session.commit()
        return jsonify(sensor_schema.dump(sensor)), 201
    
    except ValidationError as err:
        return jsonify(err.messages), 400
    except SQLAlchemyError as e:
        db.session.rollback() 
        return jsonify({"error": "An Error ocurred while saving the sensor on the database" }), 500
    
#endpoint to update a sensor
@sensor_bp.route('/sensors/<int:id>', methods=['PUT'])
def update_sensor(id):
    sensor = Sensor.query.get(id)
    if sensor:
        sensor_schema = SensorSchema()
        try:
            sensor = sensor_schema.load(request.json, instance=sensor, partial=True)
            db.session.commit()
            return jsonify(sensor_schema.dump(sensor)), 200
        except ValidationError as err:
            return jsonify(err.messages), 400
        except SQLAlchemyError as e:
            print(e)
            db.session.rollback() 
            return jsonify({"error": "An Error occurred while updating the sensor in the database"}), 500
    return jsonify({"error": "Sensor not found"}), 404

#endpoint to delete a sensor
@sensor_bp.route('/sensors/<int:id>', methods=['DELETE'])
def delete_sensor(id):
    try:
        sensor = Sensor.query.get(id)
        if sensor:
            db.session.delete(sensor)
            db.session.commit()
            return jsonify({"message": "Sensor deleted successfully"}), 204
        return jsonify({"error": "Sensor not found"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the sensor"}), 500
