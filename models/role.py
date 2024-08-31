from db import db

class Role(db.Model):
    __tablename__ = 'role'
    role_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500), nullable=False)



