from typing import override
from flask import Response
from flask_jwt_extended import current_user, jwt_required
from api_server import ApiNamespace
from flask_restx import Resource, fields

from api_server.guild_manager import GuildManager

class GuildsNamespace(ApiNamespace):
    @override
    def get_name(self) -> str:
        return 'guilds'

    @override
    def get_path(self) -> str:
        return 'guilds'

    @override
    def get_description(self) -> str:
        return 'Listing guilds.'

    @override
    def use_jwt(self):
        return True

api = GuildsNamespace()

Guild = api.namespace.model('Discord Guild simplified', {
    'id': fields.String(required=True, description='Guild ID.'),
    'name': fields.String(required=True, description='Guild name.')
})

@api.namespace.route('/')
class GuildsRoute(Resource):
    method_decorators = [jwt_required()]

    from api_server.login_manager import LoginManager
    @LoginManager.bind
    def login_manager(self) -> LoginManager: ...

    @api.namespace.doc(security="jsonWebToken")
    @api.namespace.marshal_list_with(Guild)
    def get(self):
        if current_user.id is None or current_user.id < 1: return []
        return [{ "id": guild.id, "name": guild.name } for guild in GuildManager(current_user.id).all]