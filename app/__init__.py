
from flask import Flask
from db import db
from flask_marshmallow import Marshmallow
from app.utils.error.error_handlers import register_error_handlers, setup_jwt_handlers
from app.routes.central_routes import register_blueprints
from flask import Flask
from db import db
from flask import Flask,request
from flask_marshmallow import Marshmallow
from app.routes.user_route import user_bp
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from decouple import config
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

env = config('FLASK_ENV', 'development')

app = Flask(__name__)

def init_app(config):
    # Configuration
    app.config.from_object(config)
    db.init_app(app)
    ma = Marshmallow(app)
    jwt = JWTManager(app)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Tamaño máximo (50 MB)
    

    # Synchronize changes between models and tables
    """ with app.app_context():
        db.create_all()
     """
    swagger = Swagger(app)
    register_blueprints(app)
    #app.register_blueprint(user_bp)
    # Registrar los manejadores de errores
    register_error_handlers(app)  # Aquí se usan los manejadores de errores

    CORS(app, resources={r"/*": {"origins": app.config['CORS_ORIGIN']}})
    
    setup_jwt_handlers(jwt)
    
    """ if __name__ == "__main__":
        app.run(debug=True) """
    
    return app
