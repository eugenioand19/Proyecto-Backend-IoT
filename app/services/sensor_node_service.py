
from app.models.sensor_node import SensorNode
from app.schemas.sensor_node_schema import SensorNodeSchema
from db import db
from marshmallow import ValidationError

sensor_node_schema = SensorNodeSchema()
sensor_node_schema_many = SensorNodeSchema(many=True)

def get_all_sensor_nodes():
    try:
        sensor_nodes = SensorNode.query.all()
        return sensor_node_schema_many.dump(sensor_nodes)
    except Exception as e:
        # Manejo de errores a nivel de servicio
        raise Exception("Error al obtener los nodos de sensores") from e

def get_sensor_node_by_id(sensor_node_id):
    try:
        sensor_node = SensorNode.query.get(sensor_node_id)
        if not sensor_node:
            raise ValueError("SensorNode not found")
        return sensor_node_schema.dump(sensor_node)
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception("Error al obtener el nodo de sensor") from e

def create_sensor_node(data):
    try:
        sensor_node = sensor_node_schema.load(data)  # Aquí se lanzará un ValidationError si falla
        db.session.add(sensor_node)
        db.session.commit()
        return sensor_node_schema.dump(sensor_node)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except Exception as e:
        db.session.rollback()  # Asegúrate de revertir cambios en caso de error
        raise Exception("Error al crear el nodo de sensor") from e

def update_sensor_node(sensor_node_id, data):
    try:
        sensor_node = SensorNode.query.get(sensor_node_id)
        if not sensor_node:
            raise ValueError("SensorNode not found")
        sensor_node = sensor_node_schema.load(data, instance=sensor_node, partial=True)
        db.session.commit()
        return sensor_node_schema.dump(sensor_node)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al actualizar el nodo de sensor") from e

def delete_sensor_node(sensor_node_id):
    try:
        sensor_node = SensorNode.query.get(sensor_node_id)
        if not sensor_node:
            raise ValueError("SensorNode not found")
        db.session.delete(sensor_node)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al eliminar el nodo de sensor") from e
