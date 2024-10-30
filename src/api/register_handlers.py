from api.api_webserver import ApiRequestRegister
from api.login import LoginRequest
from api.roles import RolesRequest

def register_api_handlers() -> None:
    ApiRequestRegister.register(LoginRequest)
    ApiRequestRegister.register(RolesRequest)