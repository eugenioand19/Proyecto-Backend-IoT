
from app.routes.user_route import user_bp
from app.routes.alert_route import alert_bp
from app.routes.data_history_routes import data_history_bp
from app.routes.node_route import node_bp
from app.routes.permission_route import permission_bp
from app.routes.role_route import role_bp
from app.routes.wetland_route import wetland_bp
from app.routes.sensor_route import sensor_bp
from app.routes.sensor_node_route import sensor_node_bp
from app.routes.auth_route import auth_bp
from app.routes.role_permission_route import role_permission_bp
def register_blueprints(app):
    blueprints = [
        user_bp,
        alert_bp,
        data_history_bp,
        node_bp,
        role_bp,
        wetland_bp,
        sensor_bp,
        sensor_node_bp,
        auth_bp,
        permission_bp,
        role_permission_bp
    ]
    
    # Register all blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)