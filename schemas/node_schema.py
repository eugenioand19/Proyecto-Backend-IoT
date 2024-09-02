from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from models.node import Node

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Node
        load_instance = True