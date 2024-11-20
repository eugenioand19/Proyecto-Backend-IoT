from db import db

class Sensor(db.Model):
    table_name = 'sensor'
    name= db.Column(db.String(200))
    sensor_id = db.Column(db.Integer, primary_key=True,autoincrement= True)
    type_sensor = db.Column(db.String(100))
    status = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())