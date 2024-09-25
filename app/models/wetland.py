from db import db

class Wetland(db.Model):
    table_name = 'wetland'
    wetland_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.String(100), nullable=False)
    longitude = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(5), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())