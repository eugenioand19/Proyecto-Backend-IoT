from db import db

class SensorNode(db.Model):
    table_name = 'sensor_node'
    node_id = db.Column(db.Integer)
    sensor_id = db.Column(db.Integer)
    installation_date = db.Column(db.DateTime)
    removal_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
