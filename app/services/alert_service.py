
from app.models.alert import Alert
from app.schemas.alert_schema import AlertSchema
from db import db
from marshmallow import ValidationError

alert_schema = AlertSchema()
alert_schema_many = AlertSchema(many=True)

def get_all_alerts():
    try:
        alerts = Alert.query.all()
        return alert_schema_many.dump(alerts)
    except Exception as e:
        # Manejo de errores a nivel de servicio
        raise Exception("Error al obtener los nodos de sensores") from e

def get_alert_by_id(alert_id):
    try:
        alert = Alert.query.get(alert_id)
        if not alert:
            raise ValueError("Alert not found")
        return alert_schema.dump(alert)
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception("Error al obtener el nodo de sensor") from e

def create_alert(data):
    try:
        alert = alert_schema.load(data)  # Aquí se lanzará un ValidationError si falla
        db.session.add(alert)
        db.session.commit()
        return alert_schema.dump(alert)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except Exception as e:
        db.session.rollback()  # Asegúrate de revertir cambios en caso de error
        raise Exception("Error al crear el nodo de sensor") from e

def update_alert(alert_id, data):
    try:
        alert = Alert.query.get(alert_id)
        if not alert:
            raise ValueError("Alert not found")
        alert = alert_schema.load(data, instance=alert, partial=True)
        db.session.commit()
        return alert_schema.dump(alert)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al actualizar el nodo de sensor") from e

def delete_alert(alert_id):
    try:
        alert = Alert.query.get(alert_id)
        if not alert:
            raise ValueError("Alert not found")
        db.session.delete(alert)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al eliminar el nodo de sensor") from e
