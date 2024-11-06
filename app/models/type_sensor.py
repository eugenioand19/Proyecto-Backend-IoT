from db import db

class TypeSensor(db.Model):
    table_name = 'type_sensor'
    id_type_sensor = db.Column(db.Integer, primary_key=True,autoincrement= True)
    code = db.Column(db.String(20))
    name = db.Column(db.String(50))
    unity = db.Column(db.String(50))
    