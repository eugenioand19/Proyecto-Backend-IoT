from sqlalchemy import asc, desc, or_
from app.models.node import Node
from app.models.sensor import Sensor
from app.models.sensor_node import SensorNode
from app.schemas.node_schema import NodeSchema
from app.services.wetland_service import get_wetland_by_id
from app.utils.error.error_handlers import ResourceNotFound, ValidationErrorExc
from db import db
from app.utils.success_responses import pagination_response,created_ok_message,ok_message
from app.utils.error.error_responses import bad_request_message, not_found_message,server_error_message
from marshmallow import ValidationError
node_schema = NodeSchema()
node_schema_many = NodeSchema(many=True)

def get_all_nodes(pagelink,statusList,typesList):
    try:
        
        query = Node.query

        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort, statusList=statusList, typesList=typesList)
        
        nodes_paginated = query.paginate(page=pagelink.page, per_page=pagelink.page_size, error_out=False)

        if not nodes_paginated.items:
            return not_found_message(message="Parece que aun no hay datos")
        data = node_schema_many.dump(nodes_paginated)
        
        return pagination_response(nodes_paginated.total,nodes_paginated.pages,nodes_paginated.page,nodes_paginated.per_page,data=data)
    except Exception as e:
        raise Exception(str(e))

def get_all_node_select(text_search,wetland_id=None):
    try:
        
        query = Node.query
        if wetland_id:
            if not  get_wetland_by_id(wetland_id):
                raise ResourceNotFound("Humedal no encontrado")
            
            query = query.filter(Node.wetland_id == wetland_id)
        
        if text_search:
            search_filter = or_(
                Node.name.ilike(f'%{text_search}%'),
                Node.location.ilike(f'%{text_search}%')
            )
            query = query.filter(search_filter)
        
        query = query.with_entities(Node.node_id, Node.name).all()
        if not query:
            return not_found_message(message="Parece que aun no hay datos")
        data = node_schema_many.dump(query)
        
        return ok_message(data=data)
    except ResourceNotFound as err:
        return not_found_message(entity="Humedal", details=str(err))
    except Exception as e:
        raise Exception(str(e))



def get_node_by_id(node_id):
    node = Node.query.get(node_id)
    if not node:
        raise ResourceNotFound("Nodo no encontrado")
    return node_schema.dump(node)
    
def create_node(data):
    try:
        if data.wetland_id:
            if not  get_wetland_by_id(data.wetland_id):
                raise ResourceNotFound("Humedal no encontrado")
        db.session.add(data)
        db.session.commit()
        return created_ok_message(message="El Nodo ha sido creado correctamente!")
    except ResourceNotFound as err:
        db.session.rollback()
        return not_found_message(entity='Humedal',details=str(err))

def update_node(node_id, data):
    try:
        if data.get("wetland_id"):
            if not  get_wetland_by_id(data.get("wetland_id")):
                raise ResourceNotFound("Humedal no encontrado")
        
        node = Node.query.get(node_id)
        if not node:
            raise ResourceNotFound("Node not found")
        node = node_schema.load(data, instance=node, partial=True)
        db.session.commit()
        return ok_message()
    except ResourceNotFound as err:
        return not_found_message(entity="Nodo o humedal", details=str(err))


def delete_node(node_id):
    try:
        node = Node.query.get(node_id)
        if not node:
            raise ResourceNotFound("Nodo no encontrado")
        db.session.delete(node)
        db.session.commit()
        return '',204
    except ResourceNotFound as e:
        return not_found_message(details=str(e),entity="Nodo")

def apply_filters_and_pagination(query, text_search=None, sort_order=None, statusList=None,typesList=None):
    
    
    if typesList:
        query = query.filter(or_(
            typesList == None,
            Node.node_type.in_(typesList)
        ))

    if statusList:
        query = query.filter(or_(
            statusList == None,
            Node.status.in_(statusList)
        ))
    


    if text_search:
       
        search_filter = or_(
            Node.str_MAC.ilike(f'%{text_search}%'),
            Node.location.ilike(f'%{text_search}%'),
             Node.name.ilike(f'%{text_search}%')
        )
        query = query.filter(search_filter)

    
    if sort_order.property_name:
        if sort_order.direction == 'ASC':
            query = query.order_by(asc(sort_order.property_name))
        else:
            query = query.order_by(desc(sort_order.property_name))

    return query


def assing_sensors_service(node_id, data):
    try:
        node = Node.query.get(node_id)

        if node is None:
            raise ResourceNotFound("El nodo no ha sido encontrado")
        
        # Obtener los sensores del JSON enviado
        new_sensor_ids = data.get('sensors', [])

        # Validar que todos los sensores existen
        existing_sensors = Sensor.query.filter(Sensor.sensor_id.in_(new_sensor_ids)).all()
        existing_sensor_ids = {sensor.sensor_id for sensor in existing_sensors}
        missing_sensor_ids = set(new_sensor_ids) - existing_sensor_ids

        if missing_sensor_ids:
            raise ResourceNotFound(f"Los siguientes sensores no existen: {missing_sensor_ids}")
        
        # Verificar conflictos de asignación y obtener detalles del primer conflicto
        conflicting_sensor = (
            db.session.query(SensorNode.sensor_id, SensorNode.node_id, Sensor.name.label("sensor_name"), Node.name.label("conflict_node_name"))
            .join(Sensor, Sensor.sensor_id == SensorNode.sensor_id)
            .join(Node, Node.node_id == SensorNode.node_id)
            .filter(SensorNode.sensor_id.in_(new_sensor_ids), SensorNode.node_id != node_id, SensorNode.status == "ACTIVE")
            .first()
        )

        if conflicting_sensor:
            sensor_name = conflicting_sensor.sensor_name
            sensor_id = conflicting_sensor.sensor_id
            conflict_node_name = conflicting_sensor.conflict_node_name
            current_node_name = node.name
            raise ValidationErrorExc(
                f"El sensor '{sensor_name}' ya está asignado al nodo '{conflict_node_name}'. "
                f"No se puede asignar al nodo '{current_node_name}'."
            )
        
        # Verificar los sensores ya existentes en el nodo
        existing_sensor_nodes = SensorNode.query.filter_by(node_id=node_id).all()
        existing_sensor_ids = [sensor_node.sensor_id for sensor_node in existing_sensor_nodes]
        
        # Actualizar los sensores existentes y marcar los no presentes como INACTIVO
        for sensor_node in existing_sensor_nodes:
            if sensor_node.sensor_id in new_sensor_ids:
                sensor_node.status = "ACTIVE"  # Cambiar el estado a ACTIVO
                sensor_node.installation_date = db.func.current_timestamp()  # Actualizar fecha de instalación
                sensor_node.removal_date = None  # Restablecer la fecha de remoción
            else:
                sensor_node.status = "INACTIVE"  # Cambiar el estado a INACTIVO
                sensor_node.removal_date = db.func.current_timestamp()  # Actualizar fecha de remoción
        
        # Crear nuevos registros para los sensores que no están asignados aún
        for sensor_id in new_sensor_ids:
            if sensor_id not in existing_sensor_ids:
                new_sensor_node = SensorNode(
                    node_id=node_id,
                    sensor_id=sensor_id,
                    status="ACTIVE",
                    installation_date=db.func.current_timestamp()
                )
                db.session.add(new_sensor_node)
        
        # Guardar los cambios
        db.session.commit()
        return created_ok_message(message="La asigancion se ha realizado correctamente!")
    except ResourceNotFound as nf:
        db.session.rollback()
        return not_found_message(details=str(nf))
    except ValidationErrorExc as ve:
        db.session.rollback()
        return bad_request_message(message= str(ve),details=str(ve))
    except Exception as err:
        db.session.rollback()
        error_message = ' '.join(str(err).split()[:5])
        return server_error_message(details=error_message)
    

