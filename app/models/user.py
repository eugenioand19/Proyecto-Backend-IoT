from db import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import deferred
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500))
    last_name = db.Column(db.String(500))
    email = db.Column(db.String(500))
    password = deferred(db.Column(db.String(1000)))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)


    

