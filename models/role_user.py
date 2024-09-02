from db import db

class RoleUser(db.Model):
    __tablename__ = 'role_user'
    role_user_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,  nullable=False)
    role_id = db.Column(db.Integer, nullable=False)
    