from db import db
from datetime import datetime
class DataHistory(db.Model):
    table_name = 'data_history'
    data_id = db.Column(db.Integer, primary_key=True,autoincrement= True)
    sensor_id = db.Column(db.Integer, nullable=False)
    register_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    value = db.Column(db.Double)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())