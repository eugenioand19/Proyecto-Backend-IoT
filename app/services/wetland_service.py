
from datetime import datetime,timedelta
import time
from flask import jsonify
from sqlalchemy import and_, asc, desc, func, or_,join,select
from app.models.data_history import DataHistory
from app.models.node import Node
from app.models.sensor import Sensor
from app.models.sensor_node import SensorNode
from app.models.type_sensor import TypeSensor
from app.models.user_wetland import UserWetland
from app.models.user import User
from app.models.wetland import Wetland
from app.schemas.data_history_schema import DataHistorySchema
from app.schemas.wetland_schema import WetlandSchema
from app.utils.error.error_handlers import ResourceNotFound
from app.utils.pagination.filters import apply_filters_and_pagination
from app.utils.success_responses import pagination_response,created_ok_message,ok_message
from app.utils.error.error_responses import bad_request_message, not_found_message,server_error_message
from db import db
from app.models.type_sensor import TypeSensor
from reportlab.pdfgen import canvas
import csv
from flask import make_response
from io import StringIO, BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from pytz import timezone,utc



wetland_schema = WetlandSchema()
wetland_schema_many = WetlandSchema(many=True)


def get_all_wetlands(pagelink,params=None,user_id=None):
    try:
        
        query = Wetland.query
        
        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort_order, params=params, entities=[Wetland])
        
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

def update_wetland(data):
    try:
        
        updated_wetlands = []
        # Verificar si se envió la lista de humedales
        if not isinstance(data.get("wetlands"), list):
            return bad_request_message(details="El formato de los datos es incorrecto. Se esperaba una lista de Humedales.")
        for wetland_data in data["wetlands"]:
            wetland_id = wetland_data.get("wetland_id")
            if not wetland_id:
                return bad_request_message(details="Falta el campo 'wetland_id' en uno de los wetlandes.")

            # Obtener el wetland de la base de datos
            wetland = Wetland.query.get(wetland_id)
            if not wetland:
                return not_found_message(entity="Wetland", message=f"Wetland con ID {wetland_id} no encontrado.")

            # Actualizar el wetland
            
            wetland = wetland_schema.load(wetland_data, instance=wetland, partial=True)
            
            
            updated_wetlands.append(wetland)

        # Confirmar los cambios en la base de datos
        db.session.commit()
        
        return ok_message(message=f"{len(updated_wetlands)} humedales actualizados exitosamente.")
    except ResourceNotFound as err:
        return not_found_message(entity="Wetland", details=str(err),)


def delete_wetland(data):
    try:
        # Validar que la lista de wetlandes esté presente en la petición
        wetland_ids = data.get("wetlands")
        if not wetland_ids or not isinstance(wetland_ids, list):
            return bad_request_message(details="El campo 'wetlands' debe ser una lista de IDs de wetlandes.")

        # Consultar los wetlandes que existen en la base de datos
        wetlands = Wetland.query.filter(Wetland.wetland_id.in_(wetland_ids)).all()

        # Identificar los wetlandes no encontrados
        found_ids = {wetland.wetland_id for wetland in wetlands}
        missing_ids = set(wetland_ids) - found_ids

        if missing_ids:
            return not_found_message(details=f"Humedales no encontrados: {list(missing_ids)}", entity="Wetland")

        # Eliminar los wetlandes encontrados
        for wetland in wetlands:
            db.session.delete(wetland)

        # Confirmar los cambios
        db.session.commit()

        return ok_message(message=f"{len(wetlands)} Humedales eliminados exitosamente.")
    except Exception as e:
        db.session.rollback()
        return server_error_message(details=str(e))



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
                "last_updated": row.register_date
            }
            

        if len(wetlands[wetland_id]["sensors"]) < 3:
            
            wetlands[wetland_id]["sensors"][row.sensor_code] = {
                "value": row.data_history_value,
                "name": row.sensor_name,
                "unity": row.type_sensor_unity,
                "max": row.type_sensor_max
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
                    
                    "last_updated": row.register_date
                }
                
            # Diccionario auxiliar para rastrear los nodos del humedal actual
                wetlands[wetland_id]["nodes_dict"] = {}

            # Acceso directo al nodo usando el diccionario auxiliar
            if row.node_id not in wetlands[wetland_id]["nodes_dict"]:
                node = {
                    "node_id": row.node_id,
                    "name": row.node_name,
                    "status": row.node_status,
                    "latitude": row.node_latitude,
                    "longitude": row.node_longitude,
                    "sensors": []  # Inicializa la lista de sensores vacía
                }
                # Añade el nodo a la lista de nodos y al diccionario auxiliar
                wetlands[wetland_id]["nodes"].append(node)
                wetlands[wetland_id]["nodes_dict"][row.node_id] = node
            else:
                node = wetlands[wetland_id]["nodes_dict"][row.node_id]

            # Añade el sensor a la lista de sensores del nodo
            node["sensors"].append({
                "sensor_id": row.sensor_id,
                "sensor_code": row.sensor_code,
                "value": row.data_history_value,
                "name": row.sensor_name,
                "unity": row.type_sensor_unity,
                "max": row.type_sensor_max,
                "latitude": row.sensor_latitude,
                "longitude": row.sensor_longitude
            })

        # Eliminamos el diccionario auxiliar antes de devolver la respuesta
        for wetland in wetlands.values():
            del wetland["nodes_dict"]

        if wetlands:
            wetland_details = next(iter(wetlands.values()))  # Selecciona el primer humedal
            return ok_message(data=wetland_details)
        else:
            return ok_message(data={})
        
    except ResourceNotFound as err:
        return not_found_message(details=str(err))
    

def get_wetlands_details(wetland_id=None, node_id=None,sensor_id=None, vauser_id= None,is_latest=False):
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
            func.timezone('America/Bogota',DataHistory.updated_at).label("last_updated"),
            func.timezone('America/Bogota',DataHistory.register_date).label("register_date"),
            TypeSensor.code.label("sensor_code"),
            Node.status.label("node_status"),
            TypeSensor.name.label("sensor_name"),
            TypeSensor.unity.label("type_sensor_unity"),
            TypeSensor.max_.label("type_sensor_max"),
            Sensor.latitude.label("sensor_latitude"),
            Sensor.longitude.label("sensor_longitude"),
            Node.latitude.label("node_latitude"),
            Node.longitude.label("node_longitude"),
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
        


        start_time_dt = datetime.utcfromtimestamp(float(starTime) / 1000.0).replace(tzinfo=utc)
        end_time_dt = datetime.utcfromtimestamp(float(endTime) / 1000.0).replace(tzinfo=utc)
        
        bogota_tz = timezone('America/Bogota')
        # Convertir a la zona horaria de Bogotá 
        start_time_bogota = start_time_dt.astimezone(bogota_tz) 
        end_time_bogota = end_time_dt.astimezone(bogota_tz)

        
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

def current_time_in_bogota(): 
    bogota_tz = timezone('America/Bogota') 
    
    return datetime.now(bogota_tz)

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

        if not pagelink.start_time or not pagelink.end_time:
            now = current_time_in_bogota() 
            if pagelink.start_time and not pagelink.end_time:
                start_time = pagelink.start_time
                end_time = int(now.timestamp() * 1000)
            else:
                
                # Última hora de la fecha actual 
                last_hour = now - timedelta(hours=1) 
                start_time = int(last_hour.timestamp() * 1000) 
                end_time = int(now.timestamp() * 1000)
        else:
            start_time = pagelink.start_time
            end_time=pagelink.end_time
        
        if not wetland_id  and not node_id and not sensor_id:
            sensor = (
                    db.session.query(DataHistory.sensor_id)
                    .join(Sensor, Sensor.sensor_id == DataHistory.sensor_id)
                    .filter(Sensor.status == "ACTIVE")  # Asegúrate de que el sensor esté activo
                    .order_by(DataHistory.register_date.desc())  # Selecciona el más reciente
                    .limit(1)
                    .scalar()
                )
            prov = (
                    db.session.query(
                        Wetland.wetland_id.label("wetland_id"),
                        Sensor.sensor_id.label("sensor_id"),
                        Node.node_id.label("node_id"),
                    )
                    .join(Node, Node.wetland_id == Wetland.wetland_id)
                    .join(SensorNode, (Node.node_id == SensorNode.node_id) & (SensorNode.status == 'ACTIVE'))
                    .join(Sensor, Sensor.sensor_id == SensorNode.sensor_id)
                    .join(DataHistory, DataHistory.sensor_id == Sensor.sensor_id)
                    .filter(DataHistory.sensor_id == sensor)
                    .order_by(DataHistory.register_date.desc())
                    .limit(1)
                    .first()
                )
            if not prov:
                return not_found_message(message="No se pudo obtener un sensor, nodo o humedal relacionado")
            wetland_id, node_id, sensor_id = prov.wetland_id, prov.node_id, prov.sensor_id
            
        query = get_wetlands_details(wetland_id=wetland_id, node_id=node_id, sensor_id=sensor_id, is_latest=False)
        
        query = apply_filters_reports(query=query, starTime=start_time, endTime=end_time,type_sensor=type_sensor)
        
        
        list = []

        row = query.first()
        if row:
            report = {
                "name_sensor": row.name_sensor,
                "type_sensor": row.sensor_name,
                "unity": row.type_sensor_unity
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

def wetlands_reports_endpoint(data_response,format_type):
    # Extraer parámetros
    
    
    # Llamar a la función principal para obtener los datos
    try:
        # Desempaquetar la tupla
        data, status_code = data_response

        # Verificar que la clave 'data' exista
        if 'data' not in data:
            return {"error": "Invalid data structure. Expected a 'data' key."}, 400
        
        print(format_type)
        print(data_response)
         # Normalizar el formato solicitado
        format_type = format_type.lower().strip()

        # Generar archivo CSV
        if format_type == 'csv':
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Wetland Name", "Wetland Location", "Node Name", "Node Location", "Sensor Name", "Register Date", "Value", "Type Sensor", "Unity"])
            for report in data['data']:
                writer.writerow([
                    report['wetland']['name'],
                    report['wetland']['location'],
                    report['node']['name'],
                    report['node']['location'],
                    report['sensor']['name'],
                    report['sensor']['register_date'],
                    report['sensor']['value'],
                    report['sensor']['type_sensor'],
                    report['sensor']['unity']
                ])
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers["Content-Disposition"] = "attachment; filename=wetland_reports.csv"
            response.headers["Content-type"] = "text/csv"
            return response

        # Generar archivo PDF
        elif format_type == 'pdf':
            buffer = BytesIO()

            # Configuración del PDF
            doc = SimpleDocTemplate(
                buffer,
                pagesize=landscape(letter),  # Orientación horizontal
            )
            # Agregar título en el canvas (parte superior de la página)
            # Crear título
            styles = getSampleStyleSheet()
            title = Paragraph("Reporte Humedales", styles['Title'])

            table_data = [["Nombre Humedal", "Ubicacion Humedal", "Nombre del nodo", "Ubicacion del nodo", "Nombre Sensor", "Fecha de registro", "Valor", "Tipo de Sensor", "Unidad"]]

            # Agregar los datos
            for report in data['data']:
                table_data.append([
                    report['wetland']['name'],
                    report['wetland']['location'],
                    report['node']['name'],
                    report['node']['location'],
                    report['sensor']['name'],
                    report['sensor']['register_date'].strftime('%Y-%m-%d %H:%M:%S'),  # Formatear fecha
                    report['sensor']['value'],
                    report['sensor']['type_sensor'],
                    report['sensor']['unity']
                ])

            # Crear tabla
            table = Table(table_data)

            # Estilo de la tabla
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Fondo gris para encabezado
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Texto blanco en encabezado
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Centrar texto
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fuente en encabezado
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Espaciado en encabezado
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Fondo beige para filas
                ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Bordes negros
            ])
            table.setStyle(style)

             # Agregar el título y la tabla al documento
            elements = [title, table]

            # Construir el documento
            doc.build(elements)

            # Retornar el PDF
            buffer.seek(0)
            response = make_response(buffer.getvalue())
            response.headers["Content-Disposition"] = "attachment; filename=wetland_reports.pdf"
            response.headers["Content-type"] = "application/pdf"
            return response

        else:
            return {"error": "Unsupported format type. Use 'csv' or 'pdf'."}, 400
    except Exception as e:
        return {"error": str(e)}, 500