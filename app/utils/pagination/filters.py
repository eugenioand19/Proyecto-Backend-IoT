from sqlalchemy import func, or_, and_, asc, desc


def apply_filters_and_pagination(query, text_search=None, sort_order=None, params=None, entities=None):
    
    """
    Aplica filtros, combina condiciones dinámicamente usando AND/OR, y gestiona la paginación.
    
    :param query: Consulta base de SQLAlchemy.
    :param params: Diccionario de parámetros de consulta.
    :param entity: Clase de la entidad SQLAlchemy.
    :return: Consulta con filtros, combinación AND/OR y paginación aplicados.
    """
    # Mapeo de operadores a funciones SQLAlchemy
    operator_map = {
        'ilike': lambda col, val: col.ilike(f"%{val}%"),
        'notContains': lambda col, val: ~col.ilike(f"%{val}%"),
        'eq': lambda col, val: col == val,
        'notEq': lambda col, val: col != val,
        'startsWith': lambda col, val: col.ilike(f"{val}%"),
        'endsWith': lambda col, val: col.ilike(f"%{val}"),
        'isNull': lambda col, _: col.is_(None),
        'isNotNull': lambda col, _: col.is_not(None),
        'in': lambda col, vals: col.in_(vals),
        'notIn': lambda col, vals: ~col.in_(vals)
    }


    # Obtener el operador lógico global (AND por defecto)
    logical_operator = params.get('operator', 'and').lower()
    combine_conditions = and_ if logical_operator == 'and' else or_

    # Lista para acumular filtros
    filters = []

    # Aplicar filtros dinámicamente

    # Obtener operador lógico global ('and' o 'or')
    logical_operator = params.get('operator', 'and').lower()
    combine_conditions = and_ if logical_operator == 'and' else or_

    # Obtener columnas válidas del modelo
    #valid_columns = {col.name: col for col in entity.__table__.columns}
    # Construir un mapa de columnas válido
    valid_columns = {}
    for entity in entities:
        for column in entity.__table__.columns:
            valid_columns[column.name] = column
    
    
    for field, raw_value in params.items():

            if field in ['page', 'page_size', 'sort']:  # Ignorar parámetros de control
                continue
            if field in ['from_', 'to']:
            # Manejar rangos de fechas o valores
                
                column = getattr(entity, 'created_at', None)  # Truncar la fecha
                
                if column:
                    
                    
                    if field == 'from_':
                        
                        
                        filters.append(func.date(column) >= raw_value)
                    elif field == 'to':
                        
                        filters.append(func.date(column) <= raw_value)
                        
            if field in valid_columns:
                column = valid_columns[field]
                
            
            # Procesar el valor y operador
            if field not in ('to','from_'):
                
                if '~' in raw_value:
                    
                    values_operator, operator_type = raw_value.rsplit('~', 1)

                    # Verificar si los valores tienen prefijo 'in-' y procesarlos
                    if values_operator.startswith('in-'):
                        multi_values = values_operator[3:].split('.')  # Quitar 'in-' y dividir
                    else:
                        multi_values = values_operator.split('.')  # Dividir por defecto
                    

                    if operator_type in operator_map:
                        
                        # Múltiples valores manejados por 'in' o 'notIn'
                        if operator_type in ['eq', 'notEq'] and len(multi_values) > 1:
                            operator_type = 'in' if operator_type == 'eq' else 'notIn'
                            
                            filters.append(operator_map[operator_type](column, multi_values))
                            
                        # Valores individuales o con operadores directos
                        else:
                            
                            filters.append(operator_map[operator_type](column, multi_values[0]))
        # Aplicar filtros combinados
    
    if filters:
        query = query.filter(combine_conditions(*filters))

    if text_search:
       
        search_filter = or_(
            entity.name.ilike(f'%{text_search}%')
        )
        query = query.filter(search_filter)

    if sort_order.property_name:
        if sort_order.direction == 'ASC':
            query = query.order_by(asc(sort_order.property_name))
        else:
            query = query.order_by(desc(sort_order.property_name))

    return query