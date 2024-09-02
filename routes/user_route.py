

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

@user_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    try:
        user = User.query.get(id)
        if user:
            user_schema = UserSchema()
            return jsonify(user_schema.dump(user))
        return jsonify({"error": "User not found"}), 404
    except SQLAlchemyError as e:
        print(e)
        return jsonify({"error": "An error occurred while retrieving the user"}), 500

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
        return jsonify({"error": "An Error ocurred while saving the user on the database" }), 500

#endpoint to update a user
@user_bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    if user:
        user_schema = UserSchema()
        try:
            user = user_schema.load(request.json, instance=user, partial=True)
            db.session.commit()  # No necesitas agregarlo de nuevo, solo confirmar la transacción
            return jsonify(user_schema.dump(user)), 200
        except ValidationError as err:
            return jsonify(err.messages), 400
        except SQLAlchemyError as e:
            print(e)
            db.session.rollback() 
            return jsonify({"error": "An Error occurred while updating the user in the database"}), 500
    return jsonify({"error": "User not found"}), 404

#endpoint to delete a user
@user_bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        user = User.query.get(id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": "User deleted successfully"}), 204  # Considera usar 204 No Content
        return jsonify({"error": "User not found"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the user"}), 500
