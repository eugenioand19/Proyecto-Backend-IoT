from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.services.auth_service import authenticate_user, create_tokens
from app.schemas.auth_schema import LoginSchema
auth_bp = Blueprint('auth', __name__, url_prefix="/api/auth")

@auth_bp.route('/login', methods=['POST'])
def login():

    login_schema = LoginSchema()
    validate =  login_schema.load(request.json)
    user = authenticate_user(request.json)
    if not user:
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token, refresh_token = create_tokens(user)
    return jsonify(access_token=access_token, refresh_token=refresh_token)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify(access_token=new_access_token)

