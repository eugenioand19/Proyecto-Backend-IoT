from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from models.wetland import Wetland

class WetlandSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Wetland
        load_instance = True