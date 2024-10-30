

from json import dumps
from discord import ChannelType
from nullsafe import _
from uuid import UUID
from api.api_webserver import ApiRequest
import bot
from data.guilds.guild_channel_functions import GuildChannelFunction


class ChannelsRequest(ApiRequest):
    @classmethod
    def route(cls): return 'channels'

    def get(self):
        user_uuid = self.request.args.get('user')
        if user_uuid is None: return [], 401
        user_cache = _(self.webserver.users_cache)[UUID(user_uuid)]
        if user_cache is None: return [], 401
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
        req = self.request
        user_uuid = req.args.get('user')
        if user_uuid is None: return [], 401
        user_cache = _(self.webserver.users_cache)[UUID(user_uuid)]
        if user_cache is None: return [], 401
        json = req.json
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