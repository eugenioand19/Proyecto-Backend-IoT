
from routes.user_route import user_bp
from routes.data_history_routes import data_history_bp
from routes.role_route import role_bp
from routes.role_user_route import role_user_bp
from routes.wetland_route import wetland_bp
from routes.node_route import node_bp
from routes.alert_route import alert_bp
from routes.sensor_route import sensor_bp
from routes.sensor_node_route import sensor_node_bp
def register_blueprints(app):
    blueprints = [
        user_bp,
        data_history_bp,
        role_bp,
        role_user_bp,
        wetland_bp,
        node_bp,
        alert_bp,
        sensor_bp,
        sensor_node_bp,
    ]
    
    # Register all blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
