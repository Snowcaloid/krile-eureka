from typing import override
from flask_jwt_extended import current_user
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
    from api_server.session_manager import SessionManager
    @SessionManager.bind
    def session_manager(self) -> SessionManager: ...

    @api.namespace.doc(security="jsonWebToken")
    @api.namespace.marshal_list_with(Guild)
    def get(self):
        self.session_manager.verify(api)
        return [{ "id": guild.id, "name": guild.name } for guild in GuildManager(current_user.id).all]