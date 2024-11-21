from sqlalchemy import func, or_, and_, asc, desc
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

def get_all_sensors(pagelink,params=None):
    try:
        
        query = db.session.query(Sensor.name.label("sensor_name"), Sensor.created_at,Sensor.purchase_date, Sensor.sensor_id, Sensor.status,TypeSensor.name, TypeSensor.code, Sensor.latitude, Sensor.longitude).join(Sensor, Sensor.type_sensor == TypeSensor.code)

        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort_order, params=params)
        
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

def update_sensor(sensor_id, data):
    try:
        sensor = Sensor.query.get(sensor_id)
        if not sensor:
            raise ResourceNotFound("Sensor not found")
        
        # Obtener los códigos válidos de la base de datos
        valid_codes = {type_sensor.code for type_sensor in TypeSensor.query.all()}
    
        # Validar el campo 'type_sensor'
        if data.get('type_sensor'):
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

def apply_filters_and_pagination(query, text_search=None, sort_order=None, params=None, entity=Sensor):
    
    """
    Aplica filtros, combina condiciones dinámicamente usando AND/OR, y gestiona la paginación.
    
    :param query: Consulta base de SQLAlchemy.
    :param params: Diccionario de parámetros de consulta.
    :param entity: Clase de la entidad SQLAlchemy.
    :return: Consulta con filtros, combinación AND/OR y paginación aplicados.
    """
    # Mapeo de operadores a funciones SQLAlchemy
    operator_map = {
        'ilike': lambda col, val: col.ilike(f"%{val}%"),
        'notContains': lambda col, val: ~col.ilike(f"%{val}%"),
        'eq': lambda col, val: col == val,
        'notEq': lambda col, val: col != val,
        'startsWith': lambda col, val: col.ilike(f"{val}%"),
        'endsWith': lambda col, val: col.ilike(f"%{val}"),
        'isNull': lambda col, _: col.is_(None),
        'isNotNull': lambda col, _: col.is_not(None),
        'in': lambda col, vals: col.in_(vals),
        'notIn': lambda col, vals: ~col.in_(vals)
    }


    # Obtener el operador lógico global (AND por defecto)
    logical_operator = params.get('operator', 'and').lower()
    combine_conditions = and_ if logical_operator == 'and' else or_

    # Lista para acumular filtros
    filters = []

    # Aplicar filtros dinámicamente

    # Obtener operador lógico global ('and' o 'or')
    logical_operator = params.get('operator', 'and').lower()
    combine_conditions = and_ if logical_operator == 'and' else or_

    # Obtener columnas válidas del modelo
    valid_columns = {col.name: col for col in Sensor.__table__.columns}
    
    for field, raw_value in params.items():
            if field in ['page', 'page_size', 'sort']:  # Ignorar parámetros de control
                continue
            if field in ['from_', 'to_']:
            # Manejar rangos de fechas o valores
                
                column = getattr(entity, 'created_at', None)  # Truncar la fecha
                
                if column:
                    print(field)
                    
                    if field == 'from_':
                        print(field)
                        
                        filters.append(func.date(column) >= raw_value)
                    elif field == 'to_':
                        print(field)
                        filters.append(func.date(column) <= raw_value)
                        
            if field in valid_columns:
                column = valid_columns[field]
                
            
            # Procesar el valor y operador
            if field not in ('to_','from_'):
                if '~' in raw_value:
                    
                    values_operator, operator_type = raw_value.rsplit('~', 1)

                    # Verificar si los valores tienen prefijo 'in-' y procesarlos
                    if values_operator.startswith('in-'):
                        multi_values = values_operator[3:].split('.')  # Quitar 'in-' y dividir
                    else:
                        multi_values = values_operator.split('.')  # Dividir por defecto
                    

                    if operator_type in operator_map:
                        
                        # Múltiples valores manejados por 'in' o 'notIn'
                        if operator_type in ['eq', 'notEq'] and len(multi_values) > 1:
                            operator_type = 'in' if operator_type == 'eq' else 'notIn'
                            print(operator_type,column,multi_values)
                            filters.append(operator_map[operator_type](column, multi_values))
                            
                        # Valores individuales o con operadores directos
                        else:
                            
                            filters.append(operator_map[operator_type](column, multi_values[0]))
        # Aplicar filtros combinados
    
    if filters:
        query = query.filter(combine_conditions(*filters))

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

