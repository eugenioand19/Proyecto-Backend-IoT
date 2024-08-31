from db import db

class RoleUser(db.Model):
    __tablename__ = 'role_user'
    """ role_user_id = db.Column(db.Integer, primary_key=True) """
    user_id = db.Column(db.Integer,"""  db.ForeignKey('usuario.user_id') """, nullable=False)
    role_id = db.Column(db.Integer,"""  db.ForeignKey('role.role_id') """, nullable=False)
    