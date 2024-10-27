from db import db
from app.models.sensor import Sensor
from app.models.sensor_node import SensorNode

class Node(db.Model):
    table_name = 'node'
    node_id = db.Column(db.Integer, primary_key=True,autoincrement= True)
    location = db.Column(db.String(500))
    name = db.Column(db.String(100))
    status = db.Column(db.String(50))
    last_connection = db.Column(db.DateTime)
    node_type = db.Column(db.String(50))
    str_MAC = db.Column(db.String(500))
    installation_date = db.Column(db.DateTime)
    wetland_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    permissions = db.relationship('Sensor', secondary='sensor_node', backref=db.backref('node', lazy='dynamic'))

