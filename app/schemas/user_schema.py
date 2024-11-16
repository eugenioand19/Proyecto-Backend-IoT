from marshmallow import Schema, fields, validate
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.user import User

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True


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
        sort_property = fields.Str(required=False, description="Sort property", 
                                validate=validate.OneOf(["created_at", "name", "last_name", "email", "role"]))
        sort_order = fields.Str(required=False, description="Sort order", 
                                validate=validate.OneOf(["ASC", "DESC"]))