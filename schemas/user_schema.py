from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from models.user import User

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True