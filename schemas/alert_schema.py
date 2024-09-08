from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from models.alert import Alert

class AlertSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Alert
        load_instance = True