
from sqlalchemy import asc, desc, or_
from app.models.wetland import Wetland
from app.schemas.wetland_schema import WetlandSchema
from app.utils.error.error_handlers import ResourceNotFound
from app.utils.success_responses import pagination_response,created_ok_message,ok_message
from app.utils.error.error_responses import bad_request_message, not_found_message,server_error_message
from db import db


wetland_schema = WetlandSchema()
wetland_schema_many = WetlandSchema(many=True)

def get_all_wetlands(pagelink,statusList):
    try:
        
        query = Wetland.query

        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort_order, statusList=statusList)
        
        wetlands_paginated = query.paginate(page=pagelink.page, per_page=pagelink.page_size, error_out=False)

        data = wetland_schema_many.dump(wetlands_paginated)
        
        return pagination_response(wetlands_paginated.total,wetlands_paginated.pages,wetlands_paginated.page,wetlands_paginated.per_page,data=data)
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

def apply_filters_and_pagination(query, text_search=None, sort_order=None, statusList=None):
    
    
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

    
    if sort_order.property_name:
        if sort_order.direction == 'ASC':
            query = query.order_by(asc(sort_order.property_name))
        else:
            query = query.order_by(desc(sort_order.property_name))

    return query
