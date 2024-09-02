from db import db

class Sensor(db.Model):
    table_name = 'sensor'
    sensor_id = db.Column(db.Integer, primary_key=True)
    type_sensor = db.Column(db.String(100))
    status = db.Column(db.String(100))
    purchase_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())