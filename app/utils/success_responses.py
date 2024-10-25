from app.utils.structure.response_structure import json_structure_ok, json_structure_pagination


def created_ok_message(data = {}, message = "El registro fue creado exitosamente"):
    return json_structure_ok(message= message, data = data, code=201)

def ok_message(data = {}, message = "Operacion Realizada Correctamente"):
    return json_structure_ok(message= message, data = data, code=200)

def pagination_response(total,total_pages,current_page,per_page, code = 200, message="Sucess.",data={}):
    return(json_structure_pagination(total,total_pages,current_page,per_page, code = code, message=message,data=data))