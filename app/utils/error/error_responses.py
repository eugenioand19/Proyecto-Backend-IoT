
from app.utils.structure.response_structure import json_structure_error
def forbidden_message(details="Access to this resource is forbidden."):
    return json_structure_error(message= "Usted no tiene acceso a esta ruta.",details=details, code=403)

def bad_request_message(details="Invalid request."):
    return json_structure_error(message= "Bad request",details=details, code=400)

def not_found_message(details="Not Found"):
    return json_structure_error(message= "La ruta no se encontro o no existe",details=details, code=404)

def unauthorized_message(details="Unauthorized access."):
    return json_structure_error(message= "Usted no se encuentra autorizado.",details=details, code=401)


def server_error_message(details="Internal Server Error"):
    return json_structure_error(message= "Problemas con el servidor, no eres tu, somos nosotros",details=details, code=500)


def conflict_message(details="Conflicto, registro duplicado."):
    return json_structure_error(message= "Parece que el registro que intentas crear ya existe.",details=details, code=409)


def  unprocessable_entity_message(details="Uno o mas datos no cumplen con la longitud establecida"):
    return json_structure_error(message= "Un dato no se encuentra ingresado correctamente.",details=details, code=409)

def  controlled_error_message(details="", message="",code=""):
    return json_structure_error(message= message,details=details, code=code)