
from sqlite3 import IntegrityError
from sqlalchemy import asc, desc, or_
from app.models.permission import Permission
from app.models.role import Role
from app.schemas.role_schema import RoleSchema
from app.services.permission_service import get_permission_by_id
from app.utils.error.error_handlers import ResourceNotFound
from app.utils.pagination.filters import apply_filters_and_pagination
from app.utils.success_responses import pagination_response,created_ok_message,ok_message
from app.utils.error.error_responses import bad_request_message, conflict_message, controlled_error_message, not_found_message,server_error_message
from db import db


role_schema = RoleSchema()
role_schema_many = RoleSchema(many=True)

def get_all_roles(pagelink,params=None):
    try:
        
        query = Role.query

        query = apply_filters_and_pagination(query, text_search = pagelink.text_search,sort_order=pagelink.sort_order, params=params, entities=[Role])
        
        roles_paginated = query.paginate(page=pagelink.page, per_page=pagelink.page_size, error_out=False)
        if not roles_paginated.items:
            return not_found_message(message="Parece que aun no hay datos")
        data = role_schema_many.dump(roles_paginated)
        
        return pagination_response(roles_paginated.total,roles_paginated.pages,roles_paginated.page,roles_paginated.per_page,data=data)
    except Exception as e:
        raise Exception(str(e))

def get_role_by_id(role_id):
    role = Role.query.get(role_id)
    if not role:
        raise ResourceNotFound("Rol no encontrado")
    return role_schema.dump(role)
    
def create_role(data):
    try:

        # Validar si el rol ya existe
        if Role.query.filter_by(name=data.name).first():
            return conflict_message(message="Ya existe un rol con ese nombre.")
    
        db.session.add(data)
        db.session.commit()
        return created_ok_message(message="El Rol ha sido creado correctamente!")
    except Exception as err:
        db.session.rollback()
        return server_error_message(details=str(err))

def get_all_role_select(text_search):
    try:
        
        query = Role.query
        if text_search:
       
            search_filter = or_(
                Role.name.ilike(f'%{text_search}%'),
                Role.description.ilike(f'%{text_search}%')
            )
            query = query.filter(search_filter)
        
        query = query.with_entities(Role.role_id, Role.name,Role.description).all()
        if not query:
            return not_found_message(message="Parece que aun no hay datos")
        data = role_schema_many.dump(query)
        
        return ok_message(data=data)
    except Exception as e:
        raise Exception(str(e))

def update_role(data):
    try:
        
        updated_roles = []
        # Verificar si se envió la lista de humedales
        if not isinstance(data.get("roles"), list):
            return bad_request_message(details="El formato de los datos es incorrecto. Se esperaba una lista de Roles.")
        for role_data in data["roles"]:
            role_id = role_data.get("role_id")
            if not role_id:
                return bad_request_message(details="Falta el campo 'role_id' en uno de los roles.")

            # Obtener el role de la base de datos
            role = Role.query.get(role_id)
            if not role:
                return not_found_message(entity="Role", message=f"Role con ID {role_id} no encontrado.")

            # Actualizar el role
            
            role = role_schema.load(role_data, instance=role, partial=True)
            
            
            updated_roles.append(role)

        # Confirmar los cambios en la base de datos
        db.session.commit()
        
        return ok_message(message=f"{len(updated_roles)} roles actualizados exitosamente.")
    except ResourceNotFound as err:
        return not_found_message(entity="Role", details=str(err),)


def delete_role(data):
    try:
        # Validar que la lista de rolees esté presente en la petición
        role_ids = data.get("roles")
        if not role_ids or not isinstance(role_ids, list):
            return bad_request_message(details="El campo 'roles' debe ser una lista de IDs de rolees.")

        # Consultar los rolees que existen en la base de datos
        roles = Role.query.filter(Role.role_id.in_(role_ids)).all()

        # Identificar los rolees no encontrados
        found_ids = {role.role_id for role in roles}
        missing_ids = set(role_ids) - found_ids

        if missing_ids:
            return not_found_message(message=f"Roles no encontrados: {list(missing_ids)}", entity="Role")

        # Eliminar los rolees encontrados
        for role in roles:
            db.session.delete(role)

        # Confirmar los cambios
        db.session.commit()

        return ok_message(message=f"{len(roles)} Roles eliminados exitosamente.")
    except Exception as e:
        db.session.rollback()
        return server_error_message(details=str(e))




def create_role_permission(role_id,data):
    try:

        if not get_role_by_id(role_id):
                raise ResourceNotFound("Role not found")
        
        role = Role.query.get(role_id)
        
        data = data.get('permissions', [])
        
        for item in data:
            if not get_permission_by_id(item):
                raise ResourceNotFound("Permission not found")
        
        role.permissions = Permission.query.filter(Permission.permission_id.in_(data)).all()
        
        db.session.commit()
        return created_ok_message(message="La asigancion se ha realizado correctamente!")
        
    except ResourceNotFound as e:
        return not_found_message(entity= "Rol o Permiso")
    except IntegrityError as ie:
        db.session.rollback()
        return conflict_message()
    except Exception as err:
        db.session.rollback()
        return controlled_error_message(details=str("Invalid operation"),message=str(err),code=404)