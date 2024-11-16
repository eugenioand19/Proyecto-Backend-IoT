
from datetime import datetime
import time
from flask import jsonify
from sqlalchemy import and_, asc, desc, func, or_,join,select
from app.models.data_history import DataHistory
from app.models.node import Node
from app.models.sensor import Sensor
from app.models.sensor_node import SensorNode
from app.models.type_sensor import TypeSensor
from app.models.wetland import Wetland
from app.schemas.data_history_schema import DataHistorySchema
from app.schemas.wetland_schema import WetlandSchema
from app.utils.error.error_handlers import ResourceNotFound
from app.utils.success_responses import pagination_response,created_ok_message,ok_message
from app.utils.error.error_responses import bad_request_message, not_found_message,server_error_message
from db import db
from app.models.type_sensor import TypeSensor
from sqlalchemy.orm import aliased



wetland_schema = WetlandSchema()
wetland_schema_many = WetlandSchema(many=True)


def get_all_wetlands(pagelink,statusList):
    try:
        
        query = Wetland.query

        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort_order, statusList=statusList)
        
        wetlands_paginated = query.paginate(page=pagelink.page, per_page=pagelink.page_size, error_out=False)
        if not wetlands_paginated.items:
            return not_found_message(message="Parece que aun no hay datos")
        
        data = wetland_schema_many.dump(wetlands_paginated)
        
        return pagination_response(wetlands_paginated.total,wetlands_paginated.pages,wetlands_paginated.page,wetlands_paginated.per_page,data=data)
    except Exception as e:
        raise Exception(str(e))

def get_all_wetland_select(text_search):
    try:
        
        query = Wetland.query
        if text_search:
       
            search_filter = or_(
                Wetland.name.ilike(f'%{text_search}%'),
                Wetland.location.ilike(f'%{text_search}%')
            )
            query = query.filter(search_filter)
        
        query = query.with_entities(Wetland.wetland_id, Wetland.name).all()
        if not query:
            return not_found_message(message="Parece que aun no hay datos")
        data = wetland_schema_many.dump(query)
        
        return ok_message(data=data)
    except Exception as e:
        raise Exception(str(e))

def get_wetland_by_id(wetland_id):
    wetland = Wetland.query.get(wetland_id)
    if not wetland:
        raise ResourceNotFound("Humedal no encontrado")
    return wetland_schema.dump(wetland)
    
def create_wetland(data):
    try:
        db.session.add(data)
        db.session.commit()
        return created_ok_message(message="El humedal ha sido creado correctamente!")
    except Exception as err:
        db.session.rollback()
        return server_error_message(details=str(err))

def update_wetland(wetland_id, data):
    try:

        wetland = Wetland.query.get(wetland_id)

        if not wetland:
            raise ResourceNotFound("Humedal no encontrado")
        
        wetland = wetland_schema.load(data, instance=wetland, partial=True)
        db.session.commit()
        return ok_message()
    except ResourceNotFound as e:
        db.session.rollback()
        return not_found_message(details=e,entity="Humedal")


def delete_wetland(wetland_id):
    try:
        wetland = Wetland.query.get(wetland_id)
        if not wetland:
            raise ResourceNotFound("Humedal no encontrado")
        
        db.session.delete(wetland)
        db.session.commit()
        return '',204
    except ResourceNotFound as e:
        return not_found_message(details=str(e),entity="Humedal")

def apply_filters_and_pagination(query, text_search=None, sort_order=None, statusList=None,starTime=None,endTime=None):
    
    
    if statusList:
        query = query.filter(or_(
            statusList == None,
            Wetland.status.in_(statusList)
        ))

    if text_search:
       
        search_filter = or_(
            Wetland.name.ilike(f'%{text_search}%'),
            Wetland.location.ilike(f'%{text_search}%')
        )
        query = query.filter(search_filter)

    if starTime and endTime:
        
        start_time_dt = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(starTime)/1000))
        end_time_dt = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(endTime)/1000))
        query = query.filter(DataHistory.created_at.between(start_time_dt, end_time_dt))

    if sort_order:
        if sort_order.property_name:
            if sort_order.direction == 'ASC':
                query = query.order_by(asc(sort_order.property_name))
            else:
                query = query.order_by(desc(sort_order.property_name))

    return query

def get_wetlands_overview():
    
    query= get_wetlands_details(is_latest=True)

    # Procesar y estructurar los resultados
    wetlands = {}
    for row in query:
        wetland_id = row.wetland_id
        if wetland_id not in wetlands:
            wetlands[wetland_id] = {
                "wetland_id": row.wetland_id,
                "name": row.wetland_name,
                "status": row.wetland_status,
                "location": row.wetland_location,
                "sensors": {},
                "last_updated": row.last_updated
            }
            

        if len(wetlands[wetland_id]["sensors"]) < 3:
            wetlands[wetland_id]["sensors"][row.sensor_code] = {
                "value": row.data_history_value,
                "name": row.sensor_name,
                "unity": row.type_sensor_unity
            }

    return ok_message(data=list(wetlands.values()))

def get_wetlands_overview_details(wetland_id=None, node_id=None):
    
    try:
        if wetland_id:
            get_wetland_by_id(wetland_id)
        
        if node_id:
            res = Node.query.get(node_id)
            if res is None:
                raise ResourceNotFound("Nodo no encontrado")
            
        query= get_wetlands_details(wetland_id=wetland_id,is_latest=True)

        # Procesar y estructurar los resultados
        wetlands = {}
        for row in query:
            
            wetland_id = row.wetland_id
            if wetland_id not in wetlands:
                wetlands[wetland_id] = {
                    "wetland_id": row.wetland_id,
                    "name": row.wetland_name,
                    "status": row.wetland_status,
                    "location": row.wetland_location,
                    "nodes": [],
                    
                    "last_updated": row.last_updated
                }
                
            # Diccionario auxiliar para rastrear los nodos del humedal actual
                wetlands[wetland_id]["nodes_dict"] = {}

            # Acceso directo al nodo usando el diccionario auxiliar
            if row.node_id not in wetlands[wetland_id]["nodes_dict"]:
                node = {
                    "node_id": row.node_id,
                    "name": row.node_name,
                    "sensors": []  # Inicializa la lista de sensores vacía
                }
                # Añade el nodo a la lista de nodos y al diccionario auxiliar
                wetlands[wetland_id]["nodes"].append(node)
                wetlands[wetland_id]["nodes_dict"][row.node_id] = node
            else:
                node = wetlands[wetland_id]["nodes_dict"][row.node_id]

            # Añade el sensor a la lista de sensores del nodo
            node["sensors"].append({
                "sensor_code": row.sensor_code,
                "value": row.data_history_value,
                "name": row.sensor_name,
                "unity": row.type_sensor_unity
            })

        # Eliminamos el diccionario auxiliar antes de devolver la respuesta
        for wetland in wetlands.values():
            del wetland["nodes_dict"]

        return ok_message(data=list(wetlands.values()))
    except ResourceNotFound as err:
        return not_found_message(details=str(err))
    

def get_wetlands_details(wetland_id=None, node_id=None,sensor_id=None,is_latest=False):
    # Crear una subconsulta con un alias explícito para obtener la última actualización de cada sensor
    latest = (
        db.session.query(
            DataHistory.sensor_id.label("sensor_id"),
            db.func.max(DataHistory.updated_at).label("latest_update")
        )
        .group_by(DataHistory.sensor_id)
        .subquery(name="latest")  # Asignamos el alias explícito "latest" a la subconsulta
    )
    

    # Consulta principal
    query = (
        db.session.query(
            Wetland.wetland_id.label("wetland_id"),
            Wetland.name.label("wetland_name"),
            Wetland.location.label("wetland_location"),
            Wetland.status.label("wetland_status"),
            Sensor.sensor_id.label("sensor_id"),
            Sensor.name.label("name_sensor"),
            Node.node_id.label("node_id"),
            Node.name.label("node_name"),
            Node.location.label("node_location"),
            DataHistory.value.label("data_history_value"),
            DataHistory.updated_at.label("last_updated"),
            DataHistory.register_date.label("register_date"),
            TypeSensor.code.label("sensor_code"),
            TypeSensor.name.label("sensor_name"),
            TypeSensor.unity.label("type_sensor_unity")
        )
        .join(Node, Node.wetland_id == Wetland.wetland_id)
        .join(SensorNode, (Node.node_id == SensorNode.node_id) & (SensorNode.status == 'ACTIVE'))
        .join(Sensor, Sensor.sensor_id == SensorNode.sensor_id)
        .join(TypeSensor, TypeSensor.code == Sensor.type_sensor)
        .order_by(Wetland.wetland_id)
    )
    
    if is_latest:
        query = query.join(latest, latest.c.sensor_id == Sensor.sensor_id).join(DataHistory, (DataHistory.sensor_id == Sensor.sensor_id) & (DataHistory.updated_at == latest.c.latest_update))
    else:
        query = query.join(DataHistory, (DataHistory.sensor_id == Sensor.sensor_id))
        
    # Agregar filtros dinámicos según los parámetros proporcionados
    if wetland_id is not None:
        query = query.filter(Wetland.wetland_id == wetland_id)
        
    if node_id is not None:
        query = query.filter(Node.node_id == node_id)

    if sensor_id is not None:
        query = query.filter(Sensor.sensor_id == sensor_id)

    return query

def apply_filters_reports(query,  sort_order=None,starTime=None,endTime=None, type_sensor=None):
    
    

    if starTime and endTime:
        

        start_time_dt = datetime.utcfromtimestamp(float(starTime) / 1000)
        start_time_dt = start_time_dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
        end_time_dt = datetime.utcfromtimestamp(float(endTime) / 1000)
        end_time_dt = end_time_dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        

        #start_time_dt = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(starTime)/1000))
        #end_time_dt = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(endTime)/1000))
        #print(start_time_dt)
        #print(end_time_dt)
        
        query = query.filter(DataHistory.register_date.between(start_time_dt, end_time_dt))

    if sort_order:
        if sort_order.property_name:
            if sort_order.direction == 'ASC':
                query = query.order_by(asc(sort_order.property_name))
            else:
                query = query.order_by(desc(sort_order.property_name))

    if type_sensor:
        query = query.filter(TypeSensor.code == type_sensor)

    return query

def wetlands_reports(wetland_id=None, node_id=None,sensor_id=None, pagelink=None, type_sensor = None):

    try:
        if wetland_id:
            get_wetland_by_id(wetland_id)
        
        if node_id:
            res = Node.query.get(node_id)
            if res is None:
                raise ResourceNotFound("Nodo no encontrado")

        if sensor_id: 
            sensor = Sensor.query.get(sensor_id)
            if not sensor:
                return not_found_message(entity="Sensor")
    
        query = get_wetlands_details(wetland_id=wetland_id, node_id=node_id, sensor_id=sensor_id, is_latest=False)
        
        query = apply_filters_reports(query=query, starTime=pagelink.start_time, sort_order = pagelink.page_link.sort_order, endTime=pagelink.end_time,type_sensor=type_sensor)
        
        report_paginated = query.paginate(page=pagelink.page_link.page, per_page=pagelink.page_link.page_size, error_out=False)

        if not report_paginated.items:
            return not_found_message(message="Parece que aun no hay datos")
        
        list = []

        for row in report_paginated:
            
            report={

                "wetland": {"name": row.wetland_name, "location": row.wetland_location},
                "node": {"name": row.node_name, "location":row.node_location},
                "sensor": {
                    "name": row.name_sensor,
                    "register_date": row.register_date,
                    "value": row.data_history_value,
                    "type_sensor": row.sensor_name,
                    "unity": row.type_sensor_unity
                }
            }

            list.append(report)
            

        return pagination_response(report_paginated.total,report_paginated.pages,report_paginated.page,report_paginated.per_page,data=list)
    except ResourceNotFound as rnf:
        return not_found_message(entity="Humedal, Nodo o sensor")
    
def wetland_report_graph(wetland_id=None, node_id=None,sensor_id=None, pagelink=None, type_sensor = None):
    try:
        if wetland_id:
            get_wetland_by_id(wetland_id)
        
        if node_id:
            res = Node.query.get(node_id)
            if res is None:
                raise ResourceNotFound("Nodo no encontrado")

        if sensor_id: 
            sensor = Sensor.query.get(sensor_id)
            if not sensor:
                return not_found_message(entity="Sensor")

        
        query = get_wetlands_details(wetland_id=wetland_id, node_id=node_id, sensor_id=sensor_id, is_latest=False)
        
        query = apply_filters_reports(query=query, starTime=pagelink.start_time, endTime=pagelink.end_time,type_sensor=type_sensor)
        
        list = []

        row = query.first()
        if row:
            report = {
                "name_sensor": row.name_sensor,
                "type_sensor": row.sensor_name
                
            }
            list.append(report)
        else:
            return not_found_message(message="Parece que aun no hay datos")


        
        for row in query:
            
            report={
                "sensor": {
                    "register_date": row.register_date,
                    "value": row.data_history_value
                }
            }

            list.append(report)


        return ok_message(data=list)
    except ResourceNotFound as rnf:
        return not_found_message(entity="Humedal, Nodo o sensor")