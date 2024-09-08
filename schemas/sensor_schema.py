from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from models.sensor import Sensor

class SensorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Sensor
        load_instance = True