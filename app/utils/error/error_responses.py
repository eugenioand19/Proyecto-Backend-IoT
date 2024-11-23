
from app.utils.structure.response_structure import json_structure_error
def forbidden_message(details="Access to this resource is forbidden."):
    return json_structure_error(message= "Usted no tiene acceso a esta ruta.",details=details, code=403)

def bad_request_message(details="Invalid request.",message= "Bad request"):
    return json_structure_error(message= message,details=details, code=400)

def not_found_message(entity=None, details="Not Found", message=None):
    if message is None:
        message = f"El {entity if entity else 'Elemento'} que intentas buscar no existe"
    return json_structure_error(message=message, details=details, code=404)

def unauthorized_message(details="Unauthorized access."):
    return json_structure_error(message= "Usted no se encuentra autorizado.",details=details, code=401)


def server_error_message(details="Internal Server Error",message= "Problemas con el servidor, no eres tu, somos nosotros"):
    return json_structure_error(message=message,details=details, code=500)


def conflict_message(details="Conflicto, registro duplicado."):
    return json_structure_error(message= "Parece que el registro que intentas crear ya existe.",details=details, code=409)


def  unprocessable_entity_message(details="Uno o mas datos no cumplen con la longitud establecida"):
    return json_structure_error(message= "Un dato no se encuentra ingresado correctamente.",details=details, code=409)

def  missing_jwt(details="Agregar JWT a la peticion", message="JWT es necesario",code=401):
    return json_structure_error(message= message,details=details, code=code)

def  error_invalid_token_callback(details="Token ingresado es inválido", message="Token ingresado es inválido",code=422):
    return json_structure_error(message= message,details=details, code=code)

def  error_expired_token_callback(details="Token ha expirado", message="Sesion ha expirado. Vuelva a Iniciar Sesion",code=401):
    return json_structure_error(message= message,details=details, code=code)

def  controlled_error_message(details="", message="",code=""):
    return json_structure_error(message= message,details=details, code=code)