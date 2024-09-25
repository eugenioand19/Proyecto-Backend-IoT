from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.role_user import RoleUser

class RoleuserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RoleUser
        load_instance = True