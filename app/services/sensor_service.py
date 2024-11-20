from sqlalchemy import asc, desc, or_
from app.models.sensor import Sensor
from app.models.type_sensor import TypeSensor
from app.models.sensor_node import SensorNode
from app.schemas.sensor_schema import SensorSchema, TypeSensorSchema
from app.services.node_service import get_node_by_id
from app.utils.error.error_handlers import ResourceNotFound
from db import db
from app.utils.success_responses import pagination_response,created_ok_message,ok_message
from app.utils.error.error_responses import bad_request_message, not_found_message,server_error_message
from marshmallow import ValidationError

sensor_schema = SensorSchema()
sensor_schema_many = SensorSchema(many=True)
type_sensor_schema = TypeSensorSchema(many=True)

def get_all_sensors(pagelink,statusList,typesList):
    try:
        
        query = db.session.query(Sensor.name.label("sensor_name"), Sensor.created_at,Sensor.purchase_date, Sensor.sensor_id, Sensor.status,TypeSensor.name, TypeSensor.code).join(Sensor, Sensor.type_sensor == TypeSensor.code)

        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort_order, statusList=statusList, typesList=typesList)
        
        sensors_paginated = query.paginate(page=pagelink.page, per_page=pagelink.page_size, error_out=False)

        if not sensors_paginated.items:
            return not_found_message(message="Parece que aun no hay datos")
        #data = sensor_schema_many.dump(sensors_paginated)

        data=[]

        for row in sensors_paginated:
            
            obj={

                "created_at": row.created_at,
                "name": row.sensor_name,
                "type_sensor": {
                    "name": row.name,
                    "code": row.code
                },
                "purchase_date": row.purchase_date.strftime("%Y-%m-%d") if row.purchase_date else None,
                "status" : row.status
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

def update_sensor(sensor_id, data):
    try:
        sensor = Sensor.query.get(sensor_id)
        if not sensor:
            raise ResourceNotFound("Sensor not found")
        
        # Obtener los códigos válidos de la base de datos
        valid_codes = {type_sensor.code for type_sensor in TypeSensor.query.all()}
    
        # Validar el campo 'type_sensor'
        if data.get('type_sensor') not in valid_codes:
            return not_found_message(entity='Tipos de Sensores')
        sensor = sensor_schema.load(data, instance=sensor, partial=True)
        db.session.commit()
        return ok_message()
    except ResourceNotFound as err:
        return not_found_message(entity="Sensor", details=str(err))


def delete_sensor(sensor_id):
    try:
        sensor = Sensor.query.get(sensor_id)
        if not sensor:
            raise ResourceNotFound("Sensor no encontrado")
        db.session.delete(sensor)
        db.session.commit()
        return '',204
    except ResourceNotFound as e:
        return not_found_message(details=str(e),entity="Sensor")

def apply_filters_and_pagination(query, text_search=None, sort_order=None, statusList=None,typesList=None):
    
    
    if typesList:
        query = query.filter(or_(
            typesList == None,
            Sensor.type_sensor.in_(typesList)
        ))

    if statusList:
        query = query.filter(or_(
            statusList == None,
            Sensor.status.in_(statusList)
        ))
    


    if text_search:
       
        search_filter = or_(
            Sensor.name.ilike(f'%{text_search}%')
        )
        query = query.filter(search_filter)

    
    if sort_order.property_name:
        if sort_order.direction == 'ASC':
            query = query.order_by(asc(sort_order.property_name))
        else:
            query = query.order_by(desc(sort_order.property_name))

    return query

def get_all_type_sensors():
    try:
        
        data = TypeSensor.query.all()
        data = type_sensor_schema.dump(data)
        return ok_message(data=data)
    except Exception as e:
        print(e)
        raise Exception(str(e))

