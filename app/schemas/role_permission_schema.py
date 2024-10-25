from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from marshmallow import Schema, fields, ValidationError
from app.models.role_permission import RolePermission


class RolePermissionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RolePermission
        load_instance = True


class DataSchema(Schema):
    role_id = fields.Integer(required=True)
    permission_id = fields.Integer(required=True)

class InputRolePermissionSchema(Schema):
    data = fields.List(fields.Nested(RolePermissionSchema), required=True)