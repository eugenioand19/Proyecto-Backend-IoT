

from flask import Blueprint, jsonify, request
from models.data_history import DataHistory
from schemas.data_history_schema import DataHistorySchema
from db import db
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
data_history_bp = Blueprint('data_history', __name__)

#endpoint to get all data history
@data_history_bp.route('/data_history', methods=['GET'])
def get_data_history():
    data_history = DataHistory.query.all()
    data_history_schema = DataHistorySchema(many=True)
    return jsonify(data_history_schema.dump(data_history))

#endpoint to get a data history by id
@data_history_bp.route('/data_history/<int:id>', methods=['GET'])
def get_data_history_by_id(id):
    try:
        data_history = DataHistory.query.get(id)
        if data_history:
            data_history_schema = DataHistorySchema()
            return jsonify(data_history_schema.dump(data_history))
        return jsonify({"error": "Data history not found"}), 404
    except SQLAlchemyError as e:
        print(e)
        return jsonify({"error": "An error occurred while retrieving the data history"}), 500

#endpoint to create a new data history
@data_history_bp.route('/data_history', methods=['POST'])
def create_data_history():
    data_history_schema = DataHistorySchema()
    try:
        data_history = data_history_schema.load(request.json)
        db.session.add(data_history)
        db.session.commit()
        return jsonify(data_history_schema.dump(data_history)), 201
    
    except ValidationError as err:
        return jsonify(err.messages), 400
    except SQLAlchemyError as e:
        db.session.rollback() 
        return jsonify({"error": "An Error ocurred while saving the data history on the database" }), 500
    
#endpoint to update a data history
@data_history_bp.route('/data_history/<int:id>', methods=['PUT'])
def update_data_history(id):
    data_history = DataHistory.query.get(id)
    if data_history:
        data_history_schema = DataHistorySchema()
        try:
            data_history = data_history_schema.load(request.json, instance=data_history, partial=True)
            db.session.commit()
            return jsonify(data_history_schema.dump(data_history)), 200
        except ValidationError as err:
            return jsonify(err.messages), 400
        except SQLAlchemyError as e:
            print(e)
            db.session.rollback() 
            return jsonify({"error": "An Error occurred while updating the data history in the database"}), 500
    return jsonify({"error": "Data history not found"}), 404

#endpoint to delete a data history
@data_history_bp.route('/data_history/<int:id>', methods=['DELETE'])
def delete_data_history(id):
    try:
        data_history = DataHistory.query.get(id)
        if data_history:
            db.session.delete(data_history)
            db.session.commit()
            return jsonify({"message": "Data history deleted successfully"}), 204
        return jsonify({"error": "Data history not found"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the data history"}), 500
