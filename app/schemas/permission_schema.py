from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.permission import Permission
from marshmallow import Schema, ValidationError, fields, validate

class PermissionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Permission
        load_instance = True

class PermissionQuerySchema(Schema):
    page_size = fields.Int(required=True, description="Page size", validate=validate.Range(min=1))
    page = fields.Int(required=True, description="Page number", validate=validate.Range(min=1))
    text_search = fields.Str(required=False, description="Search query")
    sort_property = fields.Str(required=False, description="Sort property", 
                               validate=validate.OneOf(["created_at", "name","description"]))
    sort_order = fields.Str(required=False, description="Sort order", 
                            validate=validate.OneOf(["ASC", "DESC"]))

class PermissionQuerySelectSchema(Schema):
    text_search = fields.Str(required=False, description="Search query")
    