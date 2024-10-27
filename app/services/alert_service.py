import datetime
from sqlalchemy import asc, desc, or_
from app.models.alert import Alert
from app.schemas.alert_schema import AlertSchema
from app.services.node_service import get_node_by_id
from app.utils.error.error_handlers import ResourceNotFound
from db import db
from app.utils.success_responses import pagination_response,created_ok_message,ok_message
from app.utils.error.error_responses import  not_found_message
from app.services.wetland_service import get_wetland_by_id
import time
alert_schema = AlertSchema()
alert_schema_many = AlertSchema(many=True)

def get_all_alerts(pagelink,statusList,severityList):
    try:
        
        query = Alert.query

        print(pagelink.page_link.text_search)
        query = apply_filters_and_pagination(query, text_search = pagelink.page_link.text_search,sort_order=pagelink.page_link.sort_order, statusList=statusList, severityList=severityList,starTime= pagelink.start_time,endTime=pagelink.end_time)
        
        alerts_paginated = query.paginate(page=pagelink.page_link.page, per_page=pagelink.page_link.page_size, error_out=False)

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

def update_alert(alert_id, data):
    try:
        if not get_node_by_id(data.get("node_id")):
            raise ResourceNotFound("Nodo no encontrado")
        
        if get_alert_by_id(alert_id):
            alert = Alert.query.get(alert_id)
        
        if not alert:
            raise ResourceNotFound("Alerta no encontrada")
        
        alert = alert_schema.load(data, instance=alert, partial=True)
        db.session.commit()
        return ok_message()
    except ResourceNotFound as err:
        return  not_found_message(entity="Nodo o Alerta", details=err)

def delete_alert(alert_id):

        alert = Alert.query.get(alert_id)
        if not alert:
            return not_found_message(entity="Alerta", details=str("Alerta no encontrada"))
        db.session.delete(alert)
        db.session.commit()
        return '',204
    
def apply_filters_and_pagination(query, text_search=None, sort_order=None, statusList=None,severityList=None,starTime=None,endTime=None):
    
    
    if severityList:
        query = query.filter(or_(
            severityList == None,
            Alert.type_alert.in_(severityList)
        ))

    if statusList:
        query = query.filter(or_(
            statusList == None,
            Alert.status.in_(statusList)
        ))
    
    if starTime and endTime:
        
        start_time_dt = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(starTime)/1000))
        end_time_dt = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(endTime)/1000))
        query = Alert.query.filter(Alert.alert_date.between(start_time_dt, end_time_dt))



    if text_search:
        search_filter = or_(
            Alert.description.ilike(f'%{text_search}%')
        )
        query = query.filter(search_filter)

    
    if sort_order.property_name:
        if sort_order.direction == 'ASC':
            query = query.order_by(asc(sort_order.property_name))
        else:
            query = query.order_by(desc(sort_order.property_name))

    return query


