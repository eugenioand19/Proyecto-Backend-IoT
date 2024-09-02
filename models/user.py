from db import db

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500))
    last_name = db.Column(db.String(500))
    email = db.Column(db.String(500))
    password = db.Column(db.String(1000))

