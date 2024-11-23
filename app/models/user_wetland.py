from db import db

class UserWetland(db.Model):
    table_name = 'user_wetland'
    user_wetland_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    wetland_id = db.Column(db.Integer, db.ForeignKey('wetland.wetland_id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
