from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.role import Role
from marshmallow import Schema, fields, validate

class RoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        load_instance = True

class RoleQuerySchema(Schema):
    page_size = fields.Int(required=True, description="Page size", validate=validate.Range(min=1))
    page = fields.Int(required=True, description="Page number", validate=validate.Range(min=1))
    text_search = fields.Str(required=False, description="Search query")
    sort_property = fields.Str(required=False, description="Sort property", 
                               validate=validate.OneOf(["created_at", "name","description"]))
    sort_order = fields.Str(required=False, description="Sort order", 
                            validate=validate.OneOf(["ASC", "DESC"]))

class PermissionListSchema(Schema):
    permissions = fields.List(fields.Integer(strict=True), required=True)

class RoleQuerySelectSchema(Schema):
    text_search = fields.Str(required=False, description="Search query")