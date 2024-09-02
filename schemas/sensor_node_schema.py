from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from models.sensor_node import SensorNode

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SensorNode
        load_instance = True