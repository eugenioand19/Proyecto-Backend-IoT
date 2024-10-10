from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError



# Step 2: Create an error handler


def register_error_handlers(app):
    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(e):
        print(e)
        return jsonify({"error": "A database error occurred"}), 400
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        print(e)
        return jsonify(e.messages), 400

    @app.errorhandler(ValueError)  # Captura de errores personalizados
    def handle_value_error(e):
        return jsonify({"error": str(e)}), 404  # Aquí puedes retornar el código de estado adecuado

    @app.errorhandler(404)
    def handle_404_error(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def handle_500_error(e):
        return jsonify({"error": "An internal server error occurred"}), 500
    

    from flask_jwt_extended import JWTManager
from flask import jsonify

def setup_jwt_handlers(jwt):

    # Manejo de token caducado
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "error": "Token ha expirado"
        }), 401

    # Manejo de token inválido
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            "error": "Token inválido"
        }), 422

    # Manejo de token faltante
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "error": "Token es necesario"
        }), 401