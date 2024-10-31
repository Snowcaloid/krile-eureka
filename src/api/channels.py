

from json import dumps
from discord import ChannelType
from nullsafe import _
from api.api_webserver import ApiRequest
import bot
from data.guilds.guild_channel_functions import GuildChannelFunction


class ChannelsRequest(ApiRequest):
    """
    ChannelsRequest API

    Endpoint:
        GET /api/channels

    Responses:
        200 OK:
        Description: Successfully retrieved the list of channels for each guild.
        Example:
            [
                {
                    "guild": 123456789012345678,
                    "channels": [
                        {
                            "id": 987654321098765432,
                            "name": "general",
                            "function": "log",
                            "event_type": "BA"
                        },
                        {
                            "id": 876543210987654321,
                            "name": "random",
                            "function": "log",
                            "event_type": "DRS"
                        }
                    ]
                }
            ]

        400 Bad Request:
        Description: Error updating the list of channels for each guild.
        Example:
            {
                "error": "Guild 123456789012345678 is not found in user cache for Example User"
            }

    Endpoint:
        POST /api/channels

    Request:
        {
            "guild": 123456789012345678,
            "channels": [
                {
                    "id": 987654321098765432,
                    "function": "log",
                    "event_type": "BASPEC",
                    "delete": false
                },
                {
                    "id": 876543210987654321,
                    "function": "log",
                    "event_type": "BOZJAALL",
                    "delete": true
                }
            ]
        }
    """
    @classmethod
    def route(cls): return 'channels'

    def get(self):
        user_cache, error = self.get_user_cache()
        if error: return error, 401
        result = []
        for cached_guild in user_cache.guilds:
            data = {'guild': cached_guild['id'], 'channels': []}
            result.append(data)
            channels_data = bot.instance.data.guilds.get(cached_guild['id']).channels
            guild = bot.instance.get_guild(cached_guild['id'])
            for channel_data in channels_data.all:
                channel = guild.get_channel(channel_data.id)
                data['channels'].append({
                    'id': channel_data.id,
                    'name': _(channel).name,
                    'function': channel_data.function.name,
                    'event_type': channel_data.event_type})
        return result

    def post(self):
        user_cache, error = self.get_user_cache()
        if error: return error, 401
        json = self.request.json
        for json_guild in _(json):
            guild_id = _(json_guild)['guild']
            if guild_id not in (guild["id"] for guild in user_cache.guilds):
                return f'Guild {_(json_guild)["guild"]} is not found in user cache for {user_cache.name}', 400
            guild_data = bot.instance.data.guilds.get(guild_id)
            guild = bot.instance.get_guild(guild_id)
            if guild is None: return f'Guild {guild_id} not found', 400
            for json_channel in _(json_guild)['channels']:
                channel_id = _(json_channel)['id']
                if channel_id is None: return f'Channel id is required for {dumps(json_channel)}', 400
                channel = guild.get_channel(channel_id)
                if channel is None: return f'Channel {channel_id} not found', 400
                if channel.type != ChannelType.text: return f'Channel {channel_id} is not a text channel', 400
                function = GuildChannelFunction[_(json_channel)['function']]
                event_type = _(json_channel)['event_type']
                channel_data = guild_data.channels.get(function, event_type)
                if channel_data is None:
                    guild_data.channels.add(channel_id, function, event_type)
                elif _(json_channel)['delete']:
                    guild_data.channels.remove(function, event_type)
                else:
                    guild_data.channels.set(channel_id, function, event_type)
        return self.get()