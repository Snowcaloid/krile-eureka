

from nullsafe import _
from uuid import UUID
from api.api_webserver import ApiRequest
import bot


class GuildsRequest(ApiRequest):
    @classmethod
    def route(cls): return 'guilds'

    def get(self):
        """Get all guilds for the user and cache them in the users_cache."""
        user_uuid = self.request.args.get('user')
        if user_uuid is None: return [], 401
        user_cache = _(self.webserver.users_cache)[UUID(user_uuid)]
        if user_cache is None: return [], 401
        user_id = user_cache.user_id
        user_cache.guilds.clear()
        result = []
        for guild_data in bot.instance.data.guilds.all:
            guild = bot.instance.get_guild(guild_data.id)
            user = guild.get_member(user_id)
            if user is None or not user.guild_permissions.administrator: continue
            result.append({'id': guild.id, 'name': guild.name})
        user_cache.guilds = result
        return result