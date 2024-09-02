from flask import Blueprint, jsonify, request
from models.role import Role
from schemas.role_schema import RoleSchema
from db import db
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
role_bp = Blueprint('role', __name__)

#endpoint to get all roles
@role_bp.route('/roles', methods=['GET'])
def get_roles():
    roles = Role.query.all()
    role_schema = RoleSchema(many=True)
    return jsonify(role_schema.dump(roles))

#endpoint to get a role by id
@role_bp.route('/roles/<int:id>', methods=['GET'])
def get_role(id):
    try:
        role = Role.query.get(id)
        if role:
            user_schema = RoleSchema()
            return jsonify(user_schema.dump(role))
        return jsonify({"error": "Role not found"}), 404
    except SQLAlchemyError as e:
        print(e)
        return jsonify({"error": "An error occurred while retrieving the role"}), 500

#endpoint to create a new role
@role_bp.route('/roles', methods=['POST'])
def create_roles():
    role_schema = RoleSchema()
    try:
        role = role_schema.load(request.json)
        db.session.add(role)
        db.session.commit()
        return jsonify(role_schema.dump(role)), 201
    
    except ValidationError as err:
        return jsonify(err.messages), 400
    except SQLAlchemyError as e:
        db.session.rollback() 
        return jsonify({"error": "An Error ocurred while saving the role on the database" }), 500
    
#endpoint to update a role
@role_bp.route('/roles/<int:id>', methods=['PUT'])
def update_role(id):
    role = Role.query.get(id)
    if role:
        role_schema = RoleSchema()
        try:
            role = role_schema.load(request.json, instance=role, partial=True)
            db.session.commit()
            return jsonify(role_schema.dump(role)), 200
        except ValidationError as err:
            return jsonify(err.messages), 400
        except SQLAlchemyError as e:
            print(e)
            db.session.rollback() 
            return jsonify({"error": "An Error occurred while updating the role in the database"}), 500
    return jsonify({"error": "Role not found"}), 404

#endpoint to delete a role
@role_bp.route('/roles/<int:id>', methods=['DELETE'])
def delete_role(id):
    try:
        role = Role.query.get(id)
        if role:
            db.session.delete(role)
            db.session.commit()
            return jsonify({"message": "Role deleted successfully"}), 204
        return jsonify({"error": "Role not found"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the role"}), 500
