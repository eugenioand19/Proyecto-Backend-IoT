
from routes.user_route import user_bp
from routes.data_history_routes import data_history_bp
from routes.role_route import role_bp
from routes.role_user_route import role_user_bp

def register_blueprints(app):
    blueprints = [
        user_bp,
        data_history_bp,
        role_bp,
        role_user_bp
        
    ]
    
    # Register all blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
