from typing import Generator, override
from flask_jwt_extended import current_user
from api_server import ApiNamespace
from flask_restx import Resource, fields

from api_server.permission_manager import PermissionManager
from api_server.guild_manager import GuildManager
from data.guilds.guild_channel import GuildChannel, GuildChannels
from utils.discord_types import API_Interaction
from data.validation.user_input import UserInput

class ChannelsNamespace(ApiNamespace):
    @override
    def get_name(self) -> str:
        return 'channels'

    @override
    def get_path(self) -> str:
        return 'channels'

    @override
    def get_description(self) -> str:
        return 'Channels management.'

    @override
    def use_jwt(self):
        return True

api = ChannelsNamespace()

ChannelModel = api.namespace.model('Configured Channel', {
    'id': fields.String(required=True, description='Chanenl ID.'),
    'name': fields.String(required=False, description='Channel name.'),
    'function': fields.String(required=False, description='Channel function.'),
    'event_type': fields.String(required=False, description='Event type restriction.')
})

def _fetch_all_channels() -> Generator[GuildChannel, None, None]:
    permissions = PermissionManager(current_user.id).calculate()
    for guild in GuildManager(current_user.id).all:
        if not permissions.for_guild(guild.id).modules.channels:
            continue
        for channel in GuildChannels(guild.id).all:
            yield channel

def _get_channel(channel_id: int = None) -> GuildChannel:
    if channel_id is None:
        channel_id = api.namespace.payload.get("id")
        if channel_id is None:
            api.namespace.abort(code=400)
    channel = next((channel for channel in _fetch_all_channels() if channel.id == channel_id), None)
    if channel is None:
        api.namespace.abort(code=404)
    return channel

@api.namespace.route('/<int:guild_id>')
class ChannelsRoute(Resource):
    from api_server.session_manager import SessionManager
    @SessionManager.bind
    def session_manager(self) -> SessionManager: ...

    @api.namespace.doc(security="jsonWebToken")
    @api.namespace.marshal_list_with(ChannelModel)
    def get(self, guild_id: int):
        self.session_manager.verify(api)
        return [ channel.marshal() for channel in _fetch_all_channels() if channel.guild_id == guild_id ]

    # @api.namespace.doc(security="jsonWebToken")
    # @api.namespace.expect(ChannelModel)
    # @api.namespace.marshal_with(ChannelModel)
    # def put(self, guild_id: int):
    #     self.session_manager.verify(api)
    #     interaction = API_Interaction(current_user.id, guild_id)
    #     event = GuildChannels(guild_id).set(event_model, interaction)
    #     return event.marshal()

# @api.namespace.route('/<int:channel_id>')
# class ChannelIDRoute(Resource):
#     from api_server.session_manager import SessionManager
#     @SessionManager.bind
#     def session_manager(self) -> SessionManager: ...

#     @UserInput.bind
#     def user_input(self) -> UserInput: ...

#     @api.namespace.doc(security="jsonWebToken")
#     @api.namespace.expect(EventModel)
#     @api.namespace.marshal_with(EventModel)
#     def patch(self, channel_id: int):
#         self.session_manager.verify(api)
#         channel = _get_channel(channel_id)
#         interaction = API_Interaction(current_user.id, channel.guild_id)
#         changes = self.user_input.channel_change(interaction, api.namespace.payload)
#         if hasattr(interaction, 'signature'):
#             api.namespace.abort(code=400, message=interaction.error_message)
#         Schedule(channel.guild_id).edit(channel.id, changes, interaction)
#         return channel.marshal()

#     @api.namespace.doc(security="jsonWebToken")
#     def delete(self, channel_id: int):
#         self.session_manager.verify(api)
#         channel = _get_channel(channel_id)
#         interaction = API_Interaction(current_user.id, channel.guild_id)
#         if not self.user_input.channel_cancellation(interaction, channel_id):
#             api.namespace.abort(code=400, message=interaction.error_message)
#         Schedule(channel.guild_id).cancel(channel.id, interaction)
#         return Response(status=200)