from db import db
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(UUID(as_uuid=True), primary_key=True,unique=True, default=uuid.uuid4, nullable=True)
    first_name = db.Column(db.String(100),nullable=False)
    second_name = db.Column(db.String(100))
    status = db.Column(db.String(10),default='active')
    last_name = db.Column(db.String(100),nullable=False)
    second_last_name = db.Column(db.String(100))
    email = db.Column(db.String(500),unique=True,nullable=False)
    password = db.Column(db.String(1000),nullable=False)
    role_id = db.Column(db.Integer,nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def set_password(self, password):
        self.password = generate_password_hash(password=password,method='pbkdf2:sha256', salt_length=16)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)


    

