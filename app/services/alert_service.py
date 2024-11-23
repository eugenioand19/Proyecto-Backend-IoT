import datetime
from sqlalchemy import asc, desc, or_
from app.models.alert import Alert
from app.schemas.alert_schema import AlertSchema
from app.services.node_service import get_node_by_id
from app.utils.error.error_handlers import ResourceNotFound
from app.utils.pagination.filters import apply_filters_and_pagination
from db import db
from app.utils.success_responses import pagination_response,created_ok_message,ok_message
from app.utils.error.error_responses import  bad_request_message, not_found_message, server_error_message

import time
alert_schema = AlertSchema()
alert_schema_many = AlertSchema(many=True)

def get_all_alerts(pagelink,params=None):
    try:
        
        query = Alert.query

        
        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort_order, params=params, entities=[Alert])
        
        alerts_paginated = query.paginate(page=pagelink.page, per_page=pagelink.page_size, error_out=False)

        if not alerts_paginated.items:
            return not_found_message(message="Parece que aun no hay datos")
        data = alert_schema_many.dump(alerts_paginated)
        
        return pagination_response(alerts_paginated.total,alerts_paginated.pages,alerts_paginated.page,alerts_paginated.per_page,data=data)
    except Exception as e:
        raise Exception(str(e))



def get_alert_by_id(node_id):
    node = Alert.query.get(node_id)
    if not node:
        raise ResourceNotFound("Alerta no encontrada")
    return alert_schema.dump(node)
    
def create_alert(data):
    try:
        
        node_id = data.node_id

        if not get_node_by_id(node_id):
            raise ResourceNotFound("Nodo no encontrado")
        
        db.session.add(data)
        db.session.commit()
        return created_ok_message(message="La alerta ha sido creado correctamente!")
    except ResourceNotFound as e:
        return not_found_message(entity="Nodo", details=str(e))

def update_alert(data):
    try:
        
        updated_alerts = []
        # Verificar si se envió la lista de humedales
        if not isinstance(data.get("alerts"), list):
            return bad_request_message(details="El formato de los datos es incorrecto. Se esperaba una lista de Alertas.")
        for alert_data in data["alerts"]:
            alert_id = alert_data.get("alert_id")
            if not alert_id:
                return bad_request_message(details="Falta el campo 'alert_id' en uno de los alertes.")

            # Obtener el alert de la base de datos
            alert = Alert.query.get(alert_id)
            if not alert:
                return not_found_message(entity="Alert", message=f"Alert con ID {alert_id} no encontrado.")

            # Actualizar el alert
            
            alert = alert_schema.load(alert_data, instance=alert, partial=True)
            
            
            updated_alerts.append(alert)

        # Confirmar los cambios en la base de datos
        db.session.commit()
        
        return ok_message(message=f"{len(updated_alerts)} Alertas actualizados exitosamente.")
    except ResourceNotFound as err:
        return not_found_message(entity="Alert", details=str(err),)


def delete_alert(data):
    try:
        # Validar que la lista de alertes esté presente en la petición
        alert_ids = data.get("alerts")
        if not alert_ids or not isinstance(alert_ids, list):
            return bad_request_message(details="El campo 'alerts' debe ser una lista de IDs de Alertas.")

        # Consultar los alertes que existen en la base de datos
        alerts = Alert.query.filter(Alert.alert_id.in_(alert_ids)).all()

        # Identificar los alertes no encontrados
        found_ids = {alert.alert_id for alert in alerts}
        missing_ids = set(alert_ids) - found_ids

        if missing_ids:
            return not_found_message(details=f"Alertas no encontradas: {list(missing_ids)}", entity="Alert")

        # Eliminar los alertes encontrados
        for alert in alerts:
            db.session.delete(alert)

        # Confirmar los cambios
        db.session.commit()

        return ok_message(message=f"{len(alerts)} Alertas eliminadas exitosamente.")
    except Exception as e:
        db.session.rollback()
        return server_error_message(details=str(e))

    


