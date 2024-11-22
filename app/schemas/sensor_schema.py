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
        exclude = ('created_at','updated_at',)
    status = fields.Str(required=True, validate=validate.OneOf(["ACTIVE","INACTIVE"]))
    type_sensor = fields.Str(required=True)

class SensorQuerySchema(Schema):
    page_size = fields.Int(required=True, description="Page size", validate=validate.Range(min=1))
    page = fields.Int(required=True, description="Page number", validate=validate.Range(min=1))
    text_search = fields.Str(required=False, description="Search query")
    sort = fields.Str(required=False, description="Sort in the format 'property.order'", validate=validate.Regexp(r'^[\w-]+\.(asc|desc)$', flags=re.IGNORECASE))
    from_ = fields.Date(data_key="from")
    to = fields.Date()

    status = fields.Str(required=False, description="Status")
    name = fields.Str(required=False, description="Name")
    type_sensor = fields.Str(required=False, description="Type Sensor")
    operator = fields.Str(required=False, description="Operator")

class TypeSensorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TypeSensor
        load_instance = True

class SensorQuerySelectSchema(Schema):
    text_search = fields.Str(required=False, description="Search query")

class SensorsUpdateSchema(Schema):
    sensors = fields.List(fields.Nested(SensorSchema), required=True)