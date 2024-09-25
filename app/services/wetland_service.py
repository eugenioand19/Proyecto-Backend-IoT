
from app.models.wetland import Wetland
from app.schemas.wetland_schema import WetlandSchema
from db import db
from marshmallow import ValidationError

wetland_schema = WetlandSchema()
wetland_schema_many = WetlandSchema(many=True)

def get_all_wetlands():
    try:
        wetlands = Wetland.query.all()
        return wetland_schema_many.dump(wetlands)
    except Exception as e:
        # Manejo de errores a nivel de servicio
        raise Exception("Error al obtener los nodos de sensores") from e

def get_wetland_by_id(wetland_id):
    try:
        wetland = Wetland.query.get(wetland_id)
        if not wetland:
            raise ValueError("Wetland not found")
        return wetland_schema.dump(wetland)
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception("Error al obtener el nodo de sensor") from e

def create_wetland(data):
    try:
        wetland = wetland_schema.load(data)  # Aquí se lanzará un ValidationError si falla
        db.session.add(wetland)
        db.session.commit()
        return wetland_schema.dump(wetland)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except Exception as e:
        db.session.rollback()  # Asegúrate de revertir cambios en caso de error
        raise Exception("Error al crear el nodo de sensor") from e

def update_wetland(wetland_id, data):
    try:
        wetland = Wetland.query.get(wetland_id)
        if not wetland:
            raise ValueError("Wetland not found")
        wetland = wetland_schema.load(data, instance=wetland, partial=True)
        db.session.commit()
        return wetland_schema.dump(wetland)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al actualizar el nodo de sensor") from e

def delete_wetland(wetland_id):
    try:
        wetland = Wetland.query.get(wetland_id)
        if not wetland:
            raise ValueError("Wetland not found")
        db.session.delete(wetland)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al eliminar el nodo de sensor") from e
