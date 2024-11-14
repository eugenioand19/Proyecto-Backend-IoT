
from app.models.data_history import DataHistory
from app.schemas.data_history_schema import DataHistorySchema
from db import db
from marshmallow import ValidationError

data_history_schema = DataHistorySchema()
data_history_schema_many = DataHistorySchema(many=True)

def get_all_data_historys():
    try:
        data_historys = DataHistory.query.all()
        return data_history_schema_many.dump(data_historys)
    except Exception as e:
        # Manejo de errores a nivel de servicio
        raise Exception("Error al obtener los nodos de sensores") from e

def get_data_history_by_id(data_history_id):
    try:
        data_history = DataHistory.query.get(data_history_id)
        if not data_history:
            raise ValueError("DataHistory not found")
        return data_history_schema.dump(data_history)
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception("Error al obtener el nodo de sensor") from e

def create_data_history(data_list):
    created_records = []
    try:
        # Itera sobre cada elemento en la lista de datos
        for data in data_list:
            # Valida y crea el objeto de historial de datos
            data_history = data_history_schema.load(data)
            db.session.add(data_history)
            created_records.append(data_history)

        db.session.commit()  # Realiza el commit después de agregar todos los registros
        return data_history_schema.dump(created_records, many=True)  # Devuelve los registros en formato JSON

    except ValidationError as ve:
        db.session.rollback()
        raise ValueError("Error en la validación de los datos") from ve

    except Exception as e:
        db.session.rollback()  # Asegúrate de revertir cambios en caso de error
        print(e)
        raise Exception("Error al crear los registros de historial de datos") from e
    
def update_data_history(data_history_id, data):
    try:
        data_history = DataHistory.query.get(data_history_id)
        if not data_history:
            raise ValueError("DataHistory not found")
        data_history = data_history_schema.load(data, instance=data_history, partial=True)
        db.session.commit()
        return data_history_schema.dump(data_history)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al actualizar el nodo de sensor") from e

def delete_data_history(data_history_id):
    try:
        data_history = DataHistory.query.get(data_history_id)
        if not data_history:
            raise ValueError("DataHistory not found")
        db.session.delete(data_history)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al eliminar el nodo de sensor") from e
