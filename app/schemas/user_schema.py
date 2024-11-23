import re
from marshmallow import Schema, fields, validate
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.user import User
from app.utils.delimited_list import DelimitedListField


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('created_at','updated_at',)
    status = fields.Str(required=False, validate=validate.OneOf(['active','inactive']))

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

    status = fields.Str(required=False, description="Status")
    first_name = fields.Str(required=False, description="First Name")
    second_name = fields.Str(required=False, description="Second Name")
    last_name = fields.Str(required=False, description="last name")
    second_last_name = fields.Str(required=False, description="Second Last name")
    email = fields.Str(required=False, description="Email")
    name = fields.Str(required=False, data_key="role",description="Rol")

class UserSchemaUp(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('created_at','updated_at','password',)
    status = fields.Str(required=True, validate=validate.OneOf('active','inactive'))

class UserUpdateSchema(Schema):
    users = fields.List(fields.Nested(UserSchemaUp), required=True)