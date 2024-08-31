
from routes.user_route import user_bp

def register_blueprints(app):
    blueprints = [
        user_bp,
    ]
    
    # Register all blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

       