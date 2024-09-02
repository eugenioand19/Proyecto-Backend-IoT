

from flask import Blueprint, jsonify, request
from models.data_history import DataHistory
from schemas.data_history_schema import DataHistorySchema
from db import db
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
data_history_bp = Blueprint('data_history', __name__)

#endpoint to get data history
@data_history_bp.route('/data_history', methods=['GET'])
def get_users():
    data_history = DataHistory.query.all()
    data_history_schema = DataHistorySchema(many=True)
    return jsonify(data_history_schema.dump(data_history))

#endpoint to create a new user
@data_history_bp.route('/data_history', methods=['POST'])
def create_data():
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
        return jsonify({"error": "An Error ocurred while saving the user on the database"}), 500

