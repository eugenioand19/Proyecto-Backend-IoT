
from app.models.node import Node
from app.schemas.node_schema import NodeSchema
from db import db
from marshmallow import ValidationError

node_schema = NodeSchema()
node_schema_many = NodeSchema(many=True)

def get_all_nodes():
    try:
        nodes = Node.query.all()
        return node_schema_many.dump(nodes)
    except Exception as e:
        # Manejo de errores a nivel de servicio
        raise Exception("Error al obtener los nodos de sensores") from e

def get_node_by_id(node_id):
    try:
        node = Node.query.get(node_id)
        if not node:
            raise ValueError("Node not found")
        return node_schema.dump(node)
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception("Error al obtener el nodo de sensor") from e

def create_node(data):
    try:
        node = node_schema.load(data)  # Aquí se lanzará un ValidationError si falla
        db.session.add(node)
        db.session.commit()
        return node_schema.dump(node)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except Exception as e:
        db.session.rollback()  # Asegúrate de revertir cambios en caso de error
        raise Exception("Error al crear el nodo de sensor") from e

def update_node(node_id, data):
    try:
        node = Node.query.get(node_id)
        if not node:
            raise ValueError("Node not found")
        node = node_schema.load(data, instance=node, partial=True)
        db.session.commit()
        return node_schema.dump(node)
    except ValidationError as ve:
        raise ValueError(str(ve)) from ve
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al actualizar el nodo de sensor") from e

def delete_node(node_id):
    try:
        node = Node.query.get(node_id)
        if not node:
            raise ValueError("Node not found")
        db.session.delete(node)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al eliminar el nodo de sensor") from e
