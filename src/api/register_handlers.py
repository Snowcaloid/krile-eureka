from api.roles import RolesHandler

def register_api_handlers() -> None:
    RolesHandler.register()