from discord import ChannelType
from nullsafe import _
from uuid import UUID
from api.api_webserver import ApiRequest
import bot


class DiscordRolesRequest(ApiRequest):
    @classmethod
    def route(cls): return 'discord/roles'

    def get(self):
        user_uuid = self.request.args.get('user')
        if user_uuid is None: return [], 401
        user_cache = _(self.webserver.users_cache)[UUID(user_uuid)]
        if user_cache is None: return [], 401
        result = []
        for cached_guild in user_cache.guilds:
            data = {'guild': cached_guild['id'], 'roles': []}
            result.append(data)
            guild = bot.instance.get_guild(cached_guild['id'])
            for role in guild.roles:
                data['roles'].append({
                    'id': role.id,
                    'name': role.name})
        return result