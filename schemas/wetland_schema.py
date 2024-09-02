from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from models.wetland import Wetland

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Wetland
        load_instance = True