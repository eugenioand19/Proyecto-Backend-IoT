from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.sensor_node import SensorNode

class SensorNodeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SensorNode
        load_instance = True