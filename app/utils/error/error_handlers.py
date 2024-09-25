from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

def register_error_handlers(app):
    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(e):
        print(e)
        return jsonify({"error": "A database error occurred"}), 500

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
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