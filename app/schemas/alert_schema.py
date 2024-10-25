from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.alert import Alert
from marshmallow import Schema, fields, validate
from app.utils.delimited_list import DelimitedListField


valid_statuses = ["ACTIVE","CLEARED","ACK","UNACK"]
valid_types = ["CRITICAL","MAJOR","MINOR","WARNING","INDETERMINATE"]
class AlertSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Alert
        load_instance = True
    status = fields.Str(required=True, validate=validate.OneOf(valid_statuses))
    severity = fields.Str(required=True, validate=validate.OneOf(valid_types))
    
class AlertQuerySchema(Schema):
    page_size = fields.Int(required=True, description="Page size", validate=validate.Range(min=1))
    page = fields.Int(required=True, description="Page number", validate=validate.Range(min=1))
    text_search = fields.Str(required=False, description="Search query")
    sort_property = fields.Str(required=False, description="Sort property", 
                               validate=validate.OneOf(["created_at", "node_id","severity","alert_date"]))
    sort_order = fields.Str(required=False, description="Sort order", 
                            validate=validate.OneOf(["ASC", "DESC"]))
    
    starTime = fields.Str(required=False, description="Star date")
    endTime = fields.Str(required=False, description="End date")
    

    # Passing the list of allowed values for validation
    statusList = DelimitedListField(
        allowed_values=valid_statuses,
        required=False,
        description="Comma-separated list of status values."
    )
    

    # Passing the list of allowed values for validation
    severityList = DelimitedListField(
        allowed_values=valid_types,
        required=False,
        description="Comma-separated list of status values."
    )
