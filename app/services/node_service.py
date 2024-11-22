from sqlalchemy import asc, desc, or_
from app.models.node import Node
from app.models.sensor import Sensor
from app.models.sensor_node import SensorNode
from app.models.wetland import Wetland
from app.schemas.node_schema import NodeSchema
from app.services.wetland_service import get_wetland_by_id
from app.utils.error.error_handlers import ResourceNotFound, ValidationErrorExc
from app.utils.pagination.filters import apply_filters_and_pagination
from db import db
from app.utils.success_responses import pagination_response,created_ok_message,ok_message
from app.utils.error.error_responses import bad_request_message, not_found_message,server_error_message
from marshmallow import ValidationError
node_schema = NodeSchema()
node_schema_many = NodeSchema(many=True)

def get_all_nodes(pagelink,params=None):
    try:
        
        query = db.session.query(Node.node_id,Node.name.label("node_name"), Node.created_at,Node.location.label("node_location"),Node.status.label("node_status"),Node.str_MAC, Node.installation_date, Node.latitude, Node.longitude, Wetland.name.label("wetland_name"), Wetland.wetland_id).join(Wetland, Wetland.wetland_id == Node.wetland_id )

        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort_order, params=params, entities=[Node])
        
        nodes_paginated = query.paginate(page=pagelink.page, per_page=pagelink.page_size, error_out=False)

        if not nodes_paginated.items:
            return not_found_message(message="Parece que aun no hay datos")
        
        data=[]

        for row in nodes_paginated:
            
            obj={
                "node_id": row.node_id,
                "created_at": row.created_at,
                "name": row.node_name,
                "wetland": {
                    "name": row.wetland_name,
                    "wetland_id": row.wetland_id
                },
                "installation_date": row.installation_date.strftime("%Y-%m-%d") if row.installation_date else None,
                "status" : row.node_status,
                "latitude": row.latitude,
                "longitude": row.longitude,
                "str_mac": row.str_MAC
            }

            data.append(obj)
        
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

def update_node(data):
    try:
        
        updated_nodes = []
        # Verificar si se envió la lista de nodos
        if not isinstance(data.get("nodes"), list):
            return bad_request_message(details="El formato de los datos es incorrecto. Se esperaba una lista de Nodos.")
        for node_data in data["nodes"]:
            node_id = node_data.get("node_id")
            if not node_id:
                return bad_request_message(details="Falta el campo 'node_id' en uno de los nodos.")

            # Obtener el node de la base de datos
            node = Node.query.get(node_id)
            if not node:
                return not_found_message(entity="Node", message=f"Nodo con ID {node_id} no encontrado.")

            # Actualizar el node
            
            node = node_schema.load(node_data, instance=node, partial=True)
            
            
            updated_nodes.append(node)

        # Confirmar los cambios en la base de datos
        db.session.commit()
        
        return ok_message(message=f"{len(updated_nodes)} Nodos actualizados exitosamente.")
    except ResourceNotFound as err:
        return not_found_message(entity="Node", details=str(err),)


def delete_node(data):
    try:
        # Validar que la lista de nodees esté presente en la petición
        node_ids = data.get("nodes")
        if not node_ids or not isinstance(node_ids, list):
            return bad_request_message(details="El campo 'nodes' debe ser una lista de IDs de nodees.")

        # Consultar los nodees que existen en la base de datos
        nodes = Node.query.filter(Node.node_id.in_(node_ids)).all()

        # Identificar los nodees no encontrados
        found_ids = {node.node_id for node in nodes}
        missing_ids = set(node_ids) - found_ids

        if missing_ids:
            return not_found_message(details=f"Nodos no encontrados: {list(missing_ids)}", entity="Node")

        # Eliminar los nodees encontrados
        for node in nodes:
            db.session.delete(node)

        # Confirmar los cambios
        db.session.commit()

        return ok_message(message=f"{len(nodes)} Nodos eliminados exitosamente.")
    except Exception as e:
        db.session.rollback()
        return server_error_message(details=str(e))




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
    

