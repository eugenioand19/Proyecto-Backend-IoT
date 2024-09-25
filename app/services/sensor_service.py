
from app.models.sensor import Sensor
from app.schemas.sensor_schema import SensorSchema
from db import db
from marshmallow import ValidationError

sensor_schema = SensorSchema()
sensor_schema_many = SensorSchema(many=True)

def get_all_sensors():
    try:
        sensors = Sensor.query.all()
        return sensor_schema_many.dump(sensors)
    except Exception as e:
        # Manejo de errores a nivel de servicio
        raise Exception("Error al obtener los nodos de sensores") from e

def get_sensor_by_id(sensor_id):
    try:
        sensor = Sensor.query.get(sensor_id)
        if not sensor:
            raise ValueError("Sensor not found")
        return sensor_schema.dump(sensor)
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception("Error al obtener el nodo de sensor") from e

def create_sensor(data):
    try:
        sensor = sensor_schema.load(data)  # Aquí se lanzará un ValidationError si falla
        db.session.add(sensor)
        db.session.commit()
        return sensor_schema.dump(sensor)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except Exception as e:
        db.session.rollback()  # Asegúrate de revertir cambios en caso de error
        raise Exception("Error al crear el nodo de sensor") from e

def update_sensor(sensor_id, data):
    try:
        sensor = Sensor.query.get(sensor_id)
        if not sensor:
            raise ValueError("Sensor not found")
        sensor = sensor_schema.load(data, instance=sensor, partial=True)
        db.session.commit()
        return sensor_schema.dump(sensor)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al actualizar el nodo de sensor") from e

def delete_sensor(sensor_id):
    try:
        sensor = Sensor.query.get(sensor_id)
        if not sensor:
            raise ValueError("Sensor not found")
        db.session.delete(sensor)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al eliminar el nodo de sensor") from e
