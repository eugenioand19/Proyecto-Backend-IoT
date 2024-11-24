import re
from marshmallow import Schema, fields, validate
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.user import User
from app.utils.delimited_list import DelimitedListField

statusList = ['active','inactive']
class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('created_at','updated_at',)
    status = fields.Str(required=False, validate=validate.OneOf(statusList))

class UserSchemaView(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('password',)
        load_instance = True
    role = fields.Str(required=False, description="Rol")


class UserQuerySchema(Schema):
    page_size = fields.Int(required=True, description="Page size", validate=validate.Range(min=1))
    page = fields.Int(required=True, description="Page number", validate=validate.Range(min=1))
    text_search = fields.Str(required=False, description="Search query")
    sort = fields.Str(required=False, description="Sort in the format 'property.order'", validate=validate.Regexp(r'^[\w-]+\.(asc|desc)$', flags=re.IGNORECASE))
    from_ = fields.Date(data_key="from")
    to = fields.Date()
    operator = fields.Str(required=False, description="Operator")
    status = fields.Str(required=False, description="Status")
    name = fields.Str(required=False, description="First Name")
    email = fields.Str(required=False, description="Email")
    role = fields.Str(required=False, data_key="role",description="Rol")

class UserSchemaUp(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('created_at','updated_at','password',)
    status = fields.Str(required=True, validate=validate.OneOf(statusList))

class UserUpdateSchema(Schema):
    users = fields.List(fields.Nested(UserSchemaUp), required=True)