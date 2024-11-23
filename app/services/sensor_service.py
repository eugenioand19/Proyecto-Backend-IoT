from sqlalchemy import func, or_, and_, asc, desc
from app.models.sensor import Sensor
from app.models.type_sensor import TypeSensor
from app.models.sensor_node import SensorNode
from app.schemas.sensor_schema import SensorSchema, TypeSensorSchema
from app.services.node_service import get_node_by_id
from app.utils.error.error_handlers import ResourceNotFound
from app.utils.pagination.filters import apply_filters_and_pagination
from db import db
from app.utils.success_responses import pagination_response,created_ok_message,ok_message
from app.utils.error.error_responses import bad_request_message, not_found_message,server_error_message
from marshmallow import ValidationError

sensor_schema = SensorSchema()
sensor_schema_many = SensorSchema(many=True)
type_sensor_schema = TypeSensorSchema(many=True)

def get_all_sensors(pagelink,params=None):
    try:
        
        query = db.session.query(Sensor.name.label("sensor_name"), Sensor.created_at,Sensor.purchase_date, Sensor.sensor_id, Sensor.status,TypeSensor.name, TypeSensor.code, Sensor.latitude, Sensor.longitude).join(Sensor, Sensor.type_sensor == TypeSensor.code)

        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort_order, params=params, entities=[Sensor])
        
        sensors_paginated = query.paginate(page=pagelink.page, per_page=pagelink.page_size, error_out=False)

        if not sensors_paginated.items:
            return not_found_message(message="Parece que aun no hay datos")
        #data = sensor_schema_many.dump(sensors_paginated)

        data=[]

        for row in sensors_paginated:
            
            obj={
                "sensor_id": row.sensor_id,
                "created_at": row.created_at,
                "name": row.sensor_name,
                "type_sensor": {
                    "name": row.name,
                    "code": row.code
                },
                "purchase_date": row.purchase_date.strftime("%Y-%m-%d") if row.purchase_date else None,
                "status" : row.status,
                "latitude": row.latitude,
                "longitude": row.longitude
            }

            data.append(obj)
            
        
        return pagination_response(sensors_paginated.total,sensors_paginated.pages,sensors_paginated.page,sensors_paginated.per_page,data=data)
    except Exception as e:
        raise Exception(str(e))

def get_all_sensor_select(text_search,node_id=None):
    try:
        
        query = Sensor.query

        if node_id:
            if not get_node_by_id(node_id=node_id):
                raise ResourceNotFound("Nodo no encontrado")
            query = (db.session.query(Sensor.sensor_id, Sensor.name,SensorNode.node_id).join(Sensor, Sensor.sensor_id == SensorNode.sensor_id).filter(SensorNode.node_id==node_id, SensorNode.status=="ACTIVE"))
            
        if text_search:
       
            search_filter = or_(
                Sensor.name.ilike(f'%{text_search}%')
            )
            query = query.filter(search_filter)
        
        query = query.with_entities(Sensor.sensor_id, Sensor.name).all()

        if not query:
            return not_found_message(message="Parece que aun no hay datos")
        data = sensor_schema_many.dump(query)
        
        return ok_message(data=data)
    except ResourceNotFound as rnf:
        return not_found_message( details=str(rnf))
    except Exception as e:
        raise Exception(str(e))

def get_sensor_by_id(sensor_id):
    sensor = Sensor.query.get(sensor_id)
    if not sensor:
        raise ResourceNotFound("Sensor no encontrado")
    return sensor_schema.dump(sensor)
    
def create_sensor(data):
    try:

        # Obtener los códigos válidos de la base de datos
        valid_codes = {type_sensor.code for type_sensor in TypeSensor.query.all()}
        
        # Validar el campo 'type_sensor'
        if data.type_sensor not in valid_codes:
            return not_found_message(entity='Tipos de Sensores')
        
        db.session.add(data)
        db.session.commit()
        return created_ok_message(message="El Sensor ha sido creado correctamente!")
    except ResourceNotFound as err:
        db.session.rollback()
        return not_found_message(entity='Se',details=str(err))

def update_sensor(data):
    try:
        
        # Verificar si se envió la lista de sensores
        if not isinstance(data.get("sensors"), list):
            return bad_request_message(details="El formato de los datos es incorrecto. Se esperaba una lista de sensores.")
        
        # Obtener los códigos válidos de la base de datos
        valid_codes = {type_sensor.code for type_sensor in TypeSensor.query.all()}

        updated_sensors = []
        
        for sensor_data in data["sensors"]:
            sensor_id = sensor_data.get("sensor_id")
            if not sensor_id:
                return bad_request_message(details="Falta el campo 'sensor_id' en uno de los sensores.")

            # Obtener el sensor de la base de datos
            sensor = Sensor.query.get(sensor_id)
            if not sensor:
                return not_found_message(entity="Sensor", message=f"Sensor con ID {sensor_id} no encontrado.")

            # Validar el campo 'type_sensor', si está presente
            if sensor_data.get("type_sensor") and sensor_data["type_sensor"] not in valid_codes:
                return bad_request_message(details=f"El tipo de sensor '{sensor_data['type_sensor']}' no es válido para el sensor con ID {sensor_id}.")

            # Actualizar el sensor
            
            sensor = sensor_schema.load(sensor_data, instance=sensor, partial=True)
            
            
            updated_sensors.append(sensor)

        # Confirmar los cambios en la base de datos
        db.session.commit()
        
        return ok_message(message=f"{len(updated_sensors)} sensores actualizados exitosamente.")
    except ResourceNotFound as err:
        return not_found_message(entity="Sensor", details=str(err),)


def delete_sensor(data):
    try:
        # Validar que la lista de sensores esté presente en la petición
        sensor_ids = data.get("sensors")
        if not sensor_ids or not isinstance(sensor_ids, list):
            return bad_request_message(details="El campo 'sensors' debe ser una lista de IDs de sensores.")

        # Consultar los sensores que existen en la base de datos
        sensors = Sensor.query.filter(Sensor.sensor_id.in_(sensor_ids)).all()

        # Identificar los sensores no encontrados
        found_ids = {sensor.sensor_id for sensor in sensors}
        missing_ids = set(sensor_ids) - found_ids

        if missing_ids:
            return not_found_message(message=f"Sensores no encontrados: {list(missing_ids)}", entity="Sensor")

        # Eliminar los sensores encontrados
        for sensor in sensors:
            db.session.delete(sensor)

        # Confirmar los cambios
        db.session.commit()

        return ok_message(message=f"{len(sensors)} sensores eliminados exitosamente.")
    except Exception as e:
        db.session.rollback()
        return server_error_message(details=str(e))



def get_all_type_sensors():
    try:
        
        data = TypeSensor.query.all()
        data = type_sensor_schema.dump(data)
        return ok_message(data=data)
    except Exception as e:
        print(e)
        raise Exception(str(e))

