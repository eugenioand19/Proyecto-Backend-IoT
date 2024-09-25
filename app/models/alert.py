from db import db

class Alert(db.Model):
    table_name = 'alert'
    alert_id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, nullable=False)
    alert_date = db.Column(db.DateTime)
    status = db.Column(db.String(100))
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
