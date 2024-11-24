from sqlalchemy import func, or_, and_, asc, desc
from app.models.user import User
from app.models.role import Role

def apply_filters_and_pagination(
    query,
    text_search=None,
    sort_order=None,
    params=None,
    entities=None
):
    # Operador lógico global (AND o OR)
    logical_operator = params.get('operator', 'and').lower()
    combine_conditions = and_ if logical_operator == 'and' else or_

    filters = []
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
    for entity in entities:
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
            if field not in ('to','from_'):
                
                # Extraer operador y valores
                if '~' in raw_value:
                    parts = raw_value.rsplit('~', 2)
                    # Asegurarse de que siempre haya 3 partes, rellenando con valores predeterminados
                    values_operator, operator_type, multi = (parts + [None] * (3 - len(parts)))
                     # Verificar si los valores tienen prefijo 'in-' y procesarlos
                    if values_operator.startswith('in-'):
                        multi_values = values_operator[3:].split('.')  # Quitar 'in-' y dividir
                    else:
                        multi_values = values_operator.split('.')  # Dividir por defecto

                    
                    
                else:
                    values_operator = raw_value
                    operator_type = 'eq'

                # Caso especial: `User` y alias `name`
                if entity == User and field == 'name':
                    if operator_type in operator_map:
                        filters.append(or_(
                            operator_map[operator_type](entity.first_name, multi_values[0]),
                            operator_map[operator_type](entity.last_name, multi_values[0])
                        ))
                    continue

                # Caso especial: `Role` y alias `role`
                if entity == Role and field == 'role':

                    if operator_type in operator_map:
                        filters.append(operator_map[operator_type](entity.code, multi_values[0]))
                    continue

                # Manejo general de columnas válidas
                valid_columns = {col.name: col for col in entity.__table__.columns}
                if field in valid_columns:
                    column = valid_columns[field]
                    print(field)
                    print(operator_type)
                    if operator_type in operator_map:
                        print(operator_type)
                        if operator_type in ['eq', 'notEq'] and len(multi_values) > 1:
                            operator_type = 'in' if operator_type == 'eq' else 'notIn'
                            filters.append(operator_map[operator_type](column, multi_values))
                        else:
                            filters.append(operator_map[operator_type](column, multi_values[0]))

    # Aplicar filtros combinados
    if filters:
        query = query.filter(combine_conditions(*filters))

    # Ordenamiento
    if sort_order and sort_order.property_name:
        if sort_order.direction == 'ASC':
            query = query.order_by(asc(sort_order.property_name))
        else:
            query = query.order_by(desc(sort_order.property_name))

    return query
