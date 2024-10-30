

from nullsafe import _
from uuid import UUID
from api.api_webserver import ApiRequest
import bot
from data.guilds.guild_pings import GuildPingType


class PingsRequest(ApiRequest):
    @classmethod
    def route(cls): return 'pings'

    def get(self):
        user_cache, error = self.get_user_cache()
        if error: return error, 401
        result = []
        for cached_guild in user_cache.guilds:
            data = {'guild': cached_guild['id'], 'pings': []}
            result.append(data)
            pings_data = bot.instance.data.guilds.get(cached_guild['id']).pings
            guild = bot.instance.get_guild(cached_guild['id'])
            for ping_data in pings_data.all:
                role = guild.get_role(ping_data.tag)
                if role is None:
                    user = guild.get_member(ping_data.tag)
                tag_type = 'role' if role is not None else 'user'
                tag_name = role.name if role is not None else _(user).display_name
                data['pings'].append({
                    'id': ping_data.id,
                    'tag_type': tag_type,
                    'tag': ping_data.tag,
                    'tag_name': tag_name,
                    'type': ping_data.type.name,
                    'event_type': ping_data.event_type})
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
            for json_ping in _(json_guild)['pings']:
                ping_id = _(json_ping)['id']
                tag_type = _(json_ping)['tag_type']
                tag = _(json_ping)['tag']
                ping_type = GuildPingType[_(json_ping)['type']]
                event_type = _(json_ping)['event_type']
                if tag_type == 'role':
                    role = guild.get_role(tag)
                    if role is None: return f'Role {tag} not found', 400
                elif tag_type == 'user':
                    user = guild.get_member(tag)
                    if user is None: return f'User {tag} not found', 400
                else:
                    return f'Invalid tag type {tag_type}', 400
                if not ping_id:
                    guild_data.pings.add_ping(ping_type, event_type, tag)
                else:
                    ping_data = guild_data.pings.get_by_id(ping_id)
                    if ping_data is None:
                        return f'Ping {ping_id} not found', 400
                    elif _(json_ping)['delete']:
                        guild_data.pings.remove_by_id(ping_id)
                    else:
                        guild_data.pings.set_by_id(ping_id, function, event_type, tag)
        return self.get()