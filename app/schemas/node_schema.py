import re
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.node import Node
from marshmallow import Schema, ValidationError, fields, validate
from app.utils.delimited_list import DelimitedListField
class NodeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Node
        exclude =('created_at','updated_at','node_type',)
        load_instance = True
    status = fields.Str(required=True, validate=validate.OneOf(["good","warning","critical"]))
    

class NodeQuerySchema(Schema):
    page_size = fields.Int(required=True, description="Page size", validate=validate.Range(min=1))
    page = fields.Int(required=True, description="Page number", validate=validate.Range(min=1))
    text_search = fields.Str(required=False, description="Search query")
    sort = fields.Str(required=False, description="Sort in the format 'property.order'", validate=validate.Regexp(r'^[\w-]+\.(asc|desc)$', flags=re.IGNORECASE))
    from_ = fields.Date(data_key="from")
    to = fields.Date()

    status = fields.Str(required=False, description="Status",validate=validate.OneOf(["good","warning","critical"]))
    name = fields.Str(required=False, description="Name")
    location = fields.Str(required=False, description="Location")
    latitude = fields.Str(required=False, description="latitude")
    longitude = fields.Str(required=False, description="longitude")
    str_MAC = fields.Str(required=False, description="str_MAC")

class SensorsListSchema(Schema):
    sensors = fields.List(fields.Integer(strict=True), required=True)

class NodeQuerySelectSchema(Schema):
    text_search = fields.Str(required=False, description="Search query")

class NodeSchemaUp(SQLAlchemyAutoSchema):
    class Meta:
        model = Node
        exclude =('created_at','updated_at','node_type',)
    status = fields.Str(required=True, validate=validate.OneOf(["good","warning","critical"]))

class NodeUpdateSchema(Schema):
    nodes = fields.List(fields.Nested(NodeSchemaUp), required=True)