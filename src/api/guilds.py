

from nullsafe import _
from api.api_webserver import ApiRequest
import bot


class GuildsRequest(ApiRequest):
    """
    GuildsRequest API

    Endpoint:
        GET /api/guilds

    Responses:
        200 OK:
        Description: Successfully retrieved the list of guilds where the user is an administrator.
                     Cache these guilds for future requests.
        Example:
            [
                {
                    "id": 123456789012345678,
                    "name": "Example Guild"
                },
                {
                    "id": 876543210987654321,
                    "name": "Another Guild"
                }
            ]

        401 Unauthorized:
        Description: Error retrieving the user cache.
        Example:
            {
                "error": "Unauthorized access"
            }
    """
    @classmethod
    def route(cls): return 'guilds'

    def get(self):
        """Get all guilds for the user and cache them in the users_cache."""
        user_cache, error = self.get_user_cache()
        if error: return error, 401
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