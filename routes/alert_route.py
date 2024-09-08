from flask import Blueprint, jsonify, request
from models.alert import Alert
from schemas.alert_schema import AlertSchema
from db import db
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
alert_bp = Blueprint('alert', __name__)

#endpoint to get all alerts
@alert_bp.route('/alerts', methods=['GET'])
def get_alerts():
    alerts = Alert.query.all()
    alert_schema = AlertSchema(many=True)
    return jsonify(alert_schema.dump(alerts))

#endpoint to get an alert by id
@alert_bp.route('/alerts/<int:id>', methods=['GET'])
def get_alert(id):
    try:
        alert = Alert.query.get(id)
        if alert:
            alert_schema = AlertSchema()
            return jsonify(alert_schema.dump(alert))
        return jsonify({"error": "Alert not found"}), 404
    except SQLAlchemyError as e:
        print(e)
        return jsonify({"error": "An error occurred while retrieving the alert"}), 500

#endpoint to create a new alert
@alert_bp.route('/alerts', methods=['POST'])
def create_alerts():
    alert_schema = AlertSchema()
    try:
        alert = alert_schema.load(request.json)
        db.session.add(alert)
        db.session.commit()
        return jsonify(alert_schema.dump(alert)), 201
    
    except ValidationError as err:
        return jsonify(err.messages), 400
    except SQLAlchemyError as e:
        db.session.rollback() 
        return jsonify({"error": "An Error ocurred while saving the alert on the database" }), 500
    
#endpoint to update an alert
@alert_bp.route('/alerts/<int:id>', methods=['PUT'])
def update_alert(id):
    alert = Alert.query.get(id)
    if alert:
        alert_schema = AlertSchema()
        try:
            alert = alert_schema.load(request.json, instance=alert, partial=True)
            db.session.commit()
            return jsonify(alert_schema.dump(alert)), 200
        except ValidationError as err:
            return jsonify(err.messages), 400
        except SQLAlchemyError as e:
            print(e)
            db.session.rollback() 
            return jsonify({"error": "An Error occurred while updating the alert in the database"}), 500
    return jsonify({"error": "Alert not found"}), 404

#endpoint to delete an alert
@alert_bp.route('/alerts/<int:id>', methods=['DELETE'])
def delete_alert(id):
    try:
        alert = Alert.query.get(id)
        if alert:
            db.session.delete(alert)
            db.session.commit()
            return jsonify({"message": "Alert deleted successfully"}), 204
        return jsonify({"error": "Alert not found"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the alert"}), 500
