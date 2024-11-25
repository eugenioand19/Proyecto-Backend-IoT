import re
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
        exclude = ('updated_at',)
    status = fields.Str(required=True, validate=validate.OneOf(valid_statuses))
    severity = fields.Str(required=True, validate=validate.OneOf(valid_types))
    
class AlertQuerySchema(Schema):
    page_size = fields.Int(required=True, description="Page size", validate=validate.Range(min=1))
    page = fields.Int(required=True, description="Page number", validate=validate.Range(min=1))
    text_search = fields.Str(required=False, description="Search query")
    sort = fields.Str(required=False, description="Sort in the format 'property.order'", validate=validate.Regexp(r'^[\w-]+\.(asc|desc)$', flags=re.IGNORECASE))
    from_ = fields.Date(data_key="from")
    to = fields.Date()
    operator = fields.Str(required=False, description="Operator")
    
    status = fields.Str(required=False, description="Status")
    description = fields.Str(required=False, description="Description")
    severity = fields.Str(required=False, description="Severity")
    title = fields.Str(required=False, description="Severity")

class AlertSchemaUp(SQLAlchemyAutoSchema):
    class Meta:
        model = Alert
        exclude = ('created_at','updated_at','severity','node_id','alert_date')
    status = fields.Str(required=True, validate=validate.OneOf(valid_statuses))

class AlertsUpdateSchema(Schema):
    alerts = fields.List(fields.Nested(AlertSchemaUp), required=True)