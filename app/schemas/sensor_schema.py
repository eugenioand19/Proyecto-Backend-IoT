from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.sensor import Sensor
from marshmallow import Schema, ValidationError, fields, validate
from app.models.type_sensor import TypeSensor
from app.utils.delimited_list import DelimitedListField
import re

class SensorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Sensor
        load_instance = True
    status = fields.Str(required=True, validate=validate.OneOf(["ACTIVE","INACTIVE"]))
    type_sensor = fields.Str(required=True)

class SensorQuerySchema(Schema):
    page_size = fields.Int(required=True, description="Page size", validate=validate.Range(min=1))
    page = fields.Int(required=True, description="Page number", validate=validate.Range(min=1))
    text_search = fields.Str(required=False, description="Search query")
    sort = fields.Str(required=False, description="Sort in the format 'property.order'", validate=validate.Regexp(r'^[\w-]+\.(asc|desc)$', flags=re.IGNORECASE))
    
    valid_statuses = ["ACTIVE","INACTIVE"]

    # Passing the list of allowed values for validation
    statusList = DelimitedListField(
        allowed_values=valid_statuses,
        description="Comma-separated list of statuses"
    )
    typesList = DelimitedListField(
        allowed_values=[type_sensor.name for type_sensor in TypeSensor.query.all()],
        description="Comma-separated list of type sensors"
    )