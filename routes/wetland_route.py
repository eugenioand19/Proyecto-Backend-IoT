from flask import Blueprint, jsonify, request
from models.wetland import Wetland
from schemas.wetland_schema import WetlandSchema
from db import db
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
wetland_bp = Blueprint('wetland', __name__)
# endpoint to get all wetlands
@wetland_bp.route('/wetlands', methods=['GET'])
def get_wetlands():
    wetlands = Wetland.query.all()
    wetland_schema = WetlandSchema(many=True)
    return jsonify(wetland_schema.dump(wetlands))

@wetland_bp.route('/wetlands/<int:id>', methods=['GET'])
def get_wetland(id):
    try:
        wetland = Wetland.query.get(id)
        if wetland:
            wetland_schema = WetlandSchema()
            return jsonify(wetland_schema.dump(wetland))
        return jsonify({"error": "Wetland not found"}), 404
    except SQLAlchemyError as e:
        print(e)
        return jsonify({"error": "An error occurred while retrieving the wetland"}), 500

# endpoint to create a new wetland
@wetland_bp.route('/wetlands', methods=['POST'])
def create_wetland():
    wetland_schema = WetlandSchema()

    try:
        wetland = wetland_schema.load(request.json)
        db.session.add(wetland)
        db.session.commit()
        return jsonify(wetland_schema.dump(wetland)), 201
    
    except ValidationError as err:
        return jsonify(err.messages), 400
    except SQLAlchemyError as e:
        db.session.rollback() 
        return jsonify({"error": "An Error occurred while saving the wetland to the database"}), 500

# endpoint to update a wetland
@wetland_bp.route('/wetlands/<int:id>', methods=['PUT'])
def update_wetland(id):
    wetland = Wetland.query.get(id)
    if wetland:
        wetland_schema = WetlandSchema()
        try:
            wetland = wetland_schema.load(request.json, instance=wetland, partial=True)
            db.session.commit()
            return jsonify(wetland_schema.dump(wetland)), 200
        except ValidationError as err:
            return jsonify(err.messages), 400
        except SQLAlchemyError as e:
            print(e)
            db.session.rollback() 
            return jsonify({"error": "An Error occurred while updating the wetland in the database"}), 500
    return jsonify({"error": "Wetland not found"}), 404

# endpoint to delete a wetland
@wetland_bp.route('/wetlands/<int:id>', methods=['DELETE'])
def delete_wetland(id):
    try:
        wetland = Wetland.query.get(id)
        if wetland:
            db.session.delete(wetland)
            db.session.commit()
            return jsonify({"message": "Wetland deleted successfully"}), 204
        return jsonify({"error": "Wetland not found"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the wetland"}), 500
