from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from models.node import Node

class NodeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Node
        load_instance = True