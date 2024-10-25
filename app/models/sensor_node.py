from db import db

class SensorNode(db.Model):
    table_name = 'sensor_node'
    sensor_node_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    node_id = db.Column(db.Integer, db.ForeignKey('node.node_id'), primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.sensor_id'), primary_key=True)
    status = db.Column(db.String(10), nullable=False, default='ACTIVE')
    installation_date = db.Column(db.DateTime)
    removal_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
