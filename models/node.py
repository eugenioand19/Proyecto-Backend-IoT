from db import db

class Node(db.Model):
    table_name = 'node'
    node_id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(500))
    status = db.Column(db.String(50))
    last_connection = db.Column(db.DateTime)
    node_type = db.Column(db.String(50))
    str_MAC = db.Column(db.String(500))
    installation_date = db.Column(db.DateTime)
    id_wetland = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())