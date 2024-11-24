import re
from marshmallow import Schema, ValidationError, fields, validate
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.wetland import Wetland
from app.utils.delimited_list import DelimitedListField


valid_statuses = ["good","warning","critical"]
class WetlandSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Wetland
        load_instance = True
        exclude = ('created_at','updated_at',)
    status = fields.Str(required=True, validate=validate.OneOf(valid_statuses))

class WetlandQuerySchema(Schema):
    page_size = fields.Int(required=True, description="Page size", validate=validate.Range(min=1))
    page = fields.Int(required=True, description="Page number", validate=validate.Range(min=1))
    text_search = fields.Str(required=False, description="Search query")
    sort = fields.Str(required=False, description="Sort in the format 'property.order'", validate=validate.Regexp(r'^[\w-]+\.(asc|desc)$', flags=re.IGNORECASE))
    from_ = fields.Date(data_key="from")
    to = fields.Date()
    operator = fields.Str(required=False, description="Operator")
    status = fields.Str(required=False, description="Status")
    name = fields.Str(required=False, description="Name")
    location = fields.Str(required=False, description="Location")
    latitude = fields.Str(required=False, description="latitude")
    longitude = fields.Str(required=False, description="longitude")
    

class WetlandQuerySelectSchema(Schema):
    text_search = fields.Str(required=False, description="Search query")

class WetlandSchemaUp(SQLAlchemyAutoSchema):
    class Meta:
        model = Wetland
        exclude = ('created_at','updated_at',)
    status = fields.Str(required=True, validate=validate.OneOf(valid_statuses))
class WetlandsUpdateSchema(Schema):
    wetlands = fields.List(fields.Nested(WetlandSchemaUp), required=True)

class WetlandListSchema(Schema):
    wetlands = fields.List(fields.Integer(strict=True), required=True)