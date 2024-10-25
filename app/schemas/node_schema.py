from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.node import Node
from marshmallow import Schema, ValidationError, fields, validate
from app.utils.delimited_list import DelimitedListField
class NodeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Node
        load_instance = True
    status = fields.Str(required=True, validate=validate.OneOf(["CRITIC","GOOD","NORMAL"]))
    node_type = fields.Str(required=True, validate=validate.OneOf(["NORMAL"]))

class NodeQuerySchema(Schema):
    page_size = fields.Int(required=True, description="Page size", validate=validate.Range(min=1))
    page = fields.Int(required=True, description="Page number", validate=validate.Range(min=1))
    text_search = fields.Str(required=False, description="Search query")
    sort_property = fields.Str(required=False, description="Sort property", 
                               validate=validate.OneOf(["created_at", "last_connection","installation_date","status", "str_MAC", "location","wetland_id"]))
    sort_order = fields.Str(required=False, description="Sort order", 
                            validate=validate.OneOf(["ASC", "DESC"]))
    
    valid_statuses = ["CRITIC","GOOD","NORMAL"]

    # Passing the list of allowed values for validation
    statusList = DelimitedListField(
        allowed_values=valid_statuses,
        required=False,
        description="Comma-separated list of status values."
    )
    valid_types = ["NORMAL"]

    # Passing the list of allowed values for validation
    TypeList = DelimitedListField(
        allowed_values=valid_types,
        required=False,
        description="Comma-separated list of status values."
    )