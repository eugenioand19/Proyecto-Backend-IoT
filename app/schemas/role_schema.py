import re
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.role import Role
from marshmallow import Schema, fields, validate

class RoleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        exclude = ('created_at','updated_at',)
        load_instance = True

class RoleQuerySchema(Schema):
    page_size = fields.Int(required=True, description="Page size", validate=validate.Range(min=1))
    page = fields.Int(required=True, description="Page number", validate=validate.Range(min=1))
    text_search = fields.Str(required=False, description="Search query")
    sort = fields.Str(required=False, description="Sort in the format 'property.order'", validate=validate.Regexp(r'^[\w-]+\.(asc|desc)$', flags=re.IGNORECASE))
    from_ = fields.Date(data_key="from")
    to = fields.Date()
    operator = fields.Str(required=False, description="Operator")
    
    code = fields.Str(required=False, description="code")
    description = fields.Str(required=False, description="Description")

class PermissionListSchema(Schema):
    permissions = fields.List(fields.Integer(strict=True), required=True)

class RoleQuerySelectSchema(Schema):
    text_search = fields.Str(required=False, description="Search query")

class RoleSchemaUp(SQLAlchemyAutoSchema):
    class Meta:
        model = Role

class RoleUpdateSchema(Schema):
    roles = fields.List(fields.Nested(RoleSchemaUp), required=True)