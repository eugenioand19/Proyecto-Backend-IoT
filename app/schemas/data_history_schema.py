from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.data_history import DataHistory

class DataHistorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DataHistory
        load_instance = True