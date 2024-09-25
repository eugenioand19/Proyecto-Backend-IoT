from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.alert import Alert

class AlertSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Alert
        load_instance = True