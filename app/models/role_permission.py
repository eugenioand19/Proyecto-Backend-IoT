from db import db

class RolePermission(db.Model):
    __tablename__ = 'role_permission'
    role_permission_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.permission_id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    