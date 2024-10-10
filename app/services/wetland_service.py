
from sqlalchemy import asc, desc, or_
from app.models.wetland import Wetland
from app.schemas.wetland_schema import WetlandSchema
from app.utils.success_responses import pagination_response
from db import db
from marshmallow import ValidationError

wetland_schema = WetlandSchema()
wetland_schema_many = WetlandSchema(many=True)

def get_all_wetlands(pagelink,statusList):
    try:
        
        query = Wetland.query

        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort_order, statusList=statusList)
        
        users_paginated = query.paginate(page=pagelink.page, per_page=pagelink.page_size, error_out=False)

        data = wetland_schema_many.dump(users_paginated)
        
        return pagination_response(users_paginated.total,users_paginated.pages,users_paginated.page,users_paginated.per_page,data=data)
    except Exception as e:
        print(e)
        raise Exception("Error al obtener los nodos de sensores") from e

def get_wetland_by_id(wetland_id):
    try:
        wetland = Wetland.query.get(wetland_id)
        if not wetland:
            raise ValueError("Wetland not found")
        return wetland_schema.dump(wetland)
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception("Error al obtener el nodo de sensor") from e

def create_wetland(data):
    try:
        wetland = wetland_schema.load(data)  # Aquí se lanzará un ValidationError si falla
        db.session.add(wetland)
        db.session.commit()
        return wetland_schema.dump(wetland)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except Exception as e:
        db.session.rollback()  # Asegúrate de revertir cambios en caso de error
        raise Exception("Error al crear el nodo de sensor") from e

def update_wetland(wetland_id, data):
    try:
        wetland = Wetland.query.get(wetland_id)
        if not wetland:
            raise ValueError("Wetland not found")
        wetland = wetland_schema.load(data, instance=wetland, partial=True)
        db.session.commit()
        return wetland_schema.dump(wetland)
    except ValidationError as ve:
        raise ValueError("Error en la validación de los datos") from ve
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al actualizar el nodo de sensor") from e

def delete_wetland(wetland_id):
    try:
        wetland = Wetland.query.get(wetland_id)
        if not wetland:
            raise ValueError("Wetland not found")
        db.session.delete(wetland)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception("Error al eliminar el nodo de sensor") from e

def apply_filters_and_pagination(query, text_search=None, sort_order=None, statusList=None):
    
    print(statusList)
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