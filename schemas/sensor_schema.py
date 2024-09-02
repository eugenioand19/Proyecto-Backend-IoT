from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from models.sensor import Sensor

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Sensor
        load_instance = True