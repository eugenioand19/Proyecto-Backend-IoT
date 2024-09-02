from flask import Blueprint, jsonify, request
from models.role_user import RoleUser
from schemas.role_user_schema import RoleuserSchema
from db import db
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
role_user_bp = Blueprint('role_user', __name__)

#endpoint to get all role_users
@role_user_bp.route('/role_users', methods=['GET'])
def get_role_users():
    role_users = RoleUser.query.all()
    role_user_schema = RoleuserSchema(many=True)
    return jsonify(role_user_schema.dump(role_users))

#endpoint to get a role_user by id
@role_user_bp.route('/role_users/<int:id>', methods=['GET'])
def get_role_user(id):
    try:
        role_user = RoleUser.query.get(id)
        if role_user:
            role_user_schema = RoleuserSchema()
            return jsonify(role_user_schema.dump(role_user))
        return jsonify({"error": "Role User not found"}), 404
    except SQLAlchemyError as e:
        print(e)
        return jsonify({"error": "An error occurred while retrieving the role user"}), 500

#endpoint to create a new role_user
@role_user_bp.route('/role_users', methods=['POST'])
def create_role_users():
    role_user_schema = RoleuserSchema()
    try:
        role_user = role_user_schema.load(request.json)
        db.session.add(role_user)
        db.session.commit()
        return jsonify(role_user_schema.dump(role_user)), 201
    
    except ValidationError as err:
        return jsonify(err.messages), 400
    except SQLAlchemyError as e:
        db.session.rollback() 
        return jsonify({"error": "An Error ocurred while saving the role user on the database" }), 500
    
#endpoint to update a role_user
@role_user_bp.route('/role_users/<int:id>', methods=['PUT'])
def update_role_user(id):
    role_user = RoleUser.query.get(id)
    if role_user:
        role_user_schema = RoleuserSchema()
        try:
            role_user = role_user_schema.load(request.json, instance=role_user, partial=True)
            db.session.commit()
            return jsonify(role_user_schema.dump(role_user)), 200
        except ValidationError as err:
            return jsonify(err.messages), 400
        except SQLAlchemyError as e:
            print(e)
            db.session.rollback() 
            return jsonify({"error": "An Error occurred while updating the role user in the database"}), 500
    return jsonify({"error": "Role User not found"}), 404

#endpoint to delete a role_user
@role_user_bp.route('/role_users/<int:id>', methods=['DELETE'])
def delete_role_user(id):
    try:
        role_user = RoleUser.query.get(id)
        if role_user:
            db.session.delete(role_user)
            db.session.commit()
            return jsonify({"message": "Role User deleted successfully"}), 204
        return jsonify({"error": "Role User not found"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the role user"}), 500
