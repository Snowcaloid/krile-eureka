from nullsafe import _
from api.api_webserver import ApiRequest
import bot


class DiscordRolesRequest(ApiRequest):
    @classmethod
    def route(cls): return 'discord/roles'

    def get(self):
        user_cache, error = self.get_user_cache()
        if error: return error, 401
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