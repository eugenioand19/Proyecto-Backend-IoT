

from flask import Blueprint, jsonify, request
from models.user import User
from schemas.user_schema import UserSchema
from db import db
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
user_bp = Blueprint('user', __name__)

#endpoint to get all users
@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_schema = UserSchema(many=True)
    return jsonify(user_schema.dump(users))

#endpoint to create a new user
@user_bp.route('/users', methods=['POST'])
def create_users():
    user_schema = UserSchema()

    try:
        user = user_schema.load(request.json)
        db.session.add(user)
        db.session.commit()
        return jsonify(user_schema.dump(user)), 201
    
    except ValidationError as err:
        return jsonify(err.messages), 400
    except SQLAlchemyError as e:
       
        db.session.rollback() 
        return jsonify({"error": "An Error ocurred while saving the user on the database"}), 500



