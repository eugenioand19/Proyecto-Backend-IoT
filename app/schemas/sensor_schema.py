from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.sensor import Sensor
from marshmallow import Schema, ValidationError, fields, validate
from app.models.type_sensor import TypeSensor
from app.utils.delimited_list import DelimitedListField
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
    sort_property = fields.Str(required=False, description="Sort property", 
                               validate=validate.OneOf(["created_at", "name"]))
    sort_order = fields.Str(required=False, description="Sort order", 
                            validate=validate.OneOf(["ASC", "DESC"]))
    
    valid_statuses = ["ACTIVE","INACTIVE"]

    # Passing the list of allowed values for validation
    statusList = DelimitedListField(
        allowed_values=valid_statuses,
        required=False,
        description="Comma-separated list of status values."
    )
    valid_types = ["PH","OD","TEMP","TURB","CAUD_EN","CAUD_SAL"]

    # Passing the list of allowed values for validation
    typesList = DelimitedListField(
        allowed_values=valid_types,
        required=False,
        description="Comma-separated list of status values."
    )

class TypeSensorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TypeSensor
        load_instance = True