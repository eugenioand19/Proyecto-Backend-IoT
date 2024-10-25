from db import db
from app.models.role_permission import RolePermission
from app.models.permission import Permission

class Role(db.Model):
    __tablename__ = 'role'
    role_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    permissions = db.relationship('Permission', secondary='role_permission', backref=db.backref('roles', lazy='dynamic'))
 
    




