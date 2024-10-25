from sqlalchemy import asc, desc, or_
from app.models.node import Node
from app.models.sensor_node import SensorNode
from app.schemas.node_schema import NodeSchema
from app.utils.error.error_handlers import ResourceNotFound
from db import db
from app.utils.success_responses import pagination_response,created_ok_message,ok_message
from app.utils.error.error_responses import bad_request_message, not_found_message,server_error_message
from marshmallow import ValidationError
from app.services.wetland_service import get_wetland_by_id
node_schema = NodeSchema()
node_schema_many = NodeSchema(many=True)

def get_all_nodes(pagelink,statusList,typesList):
    try:
        
        query = Node.query

        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort_order, statusList=statusList, typesList=typesList)
        
        nodes_paginated = query.paginate(page=pagelink.page, per_page=pagelink.page_size, error_out=False)

        data = node_schema_many.dump(nodes_paginated)
        
        return pagination_response(nodes_paginated.total,nodes_paginated.pages,nodes_paginated.page,nodes_paginated.per_page,data=data)
    except Exception as e:
        raise Exception(str(e))



def get_node_by_id(node_id):
    try:
        node = Node.query.get(node_id)
        if not node:
            raise ResourceNotFound("Nodo no encontrado")
        return (node_schema.dump(node))
    except ResourceNotFound as e:
        return not_found_message(details=e,entity="Nodo")
    
def create_node(data):
    try:
         
        if not  get_wetland_by_id(data.wetland_id):
            raise Exception("Wetland not found")
        db.session.add(data)
        db.session.commit()
        return created_ok_message(message="El Nodo ha sido creado correctamente!")
    except Exception as err:
        db.session.rollback()
        return server_error_message(details=str(err))

def update_node(node_id, data):
    try:
        if not  get_wetland_by_id(data.get('wetland_id')):
            raise Exception("golasd")
        node = Node.query.get(node_id)
        if not node:
            raise ValueError("Node not found")
        node = node_schema.load(data, instance=node, partial=True)
        db.session.commit()
        return ok_message()
    except ValueError as err:
        raise ValueError(err)
    except Exception as e:
        db.session.rollback()
        raise Exception(str(e)) 

def delete_node(node_id):
    try:
        node = Node.query.get(node_id)
        if not node:
            raise ValueError("Node not found")
        db.session.delete(node)
        db.session.commit()
        return True
    except ValueError as err:
        db.session.rollback()
        raise ValueError("Node not found")
    except Exception as e:
        db.session.rollback()
        raise Exception(str(e))

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
            Node.location.ilike(f'%{text_search}%')
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
        
        # Obtener los sensores del JSON enviado
        new_sensor_ids = data.get('sensors', [])

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
    except Exception as err:
        db.session.rollback()
        return server_error_message(details=str(err))
    

