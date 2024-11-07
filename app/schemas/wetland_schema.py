from marshmallow import Schema, ValidationError, fields, validate
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.wetland import Wetland
from app.utils.delimited_list import DelimitedListField


valid_statuses = ["CRITIC","GOOD","NORMAL"]
class WetlandSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Wetland
        load_instance = True
    status = fields.Str(required=True, validate=validate.OneOf(valid_statuses))

class WetlandQuerySchema(Schema):
    page_size = fields.Int(required=True, description="Page size", validate=validate.Range(min=1))
    page = fields.Int(required=True, description="Page number", validate=validate.Range(min=1))
    text_search = fields.Str(required=False, description="Search query")
    sort_property = fields.Str(required=False, description="Sort property", 
                               validate=validate.OneOf(["created_at", "status", "name", "location"]))
    sort_order = fields.Str(required=False, description="Sort order", 
                            validate=validate.OneOf(["ASC", "DESC"]))

    

    # Passing the list of allowed values for validation
    statusList = DelimitedListField(
        allowed_values=valid_statuses,
        required=False,
        description="Comma-separated list of status values."
    )

class WetlandQuerySelectSchema(Schema):
    text_search = fields.Str(required=False, description="Search query")