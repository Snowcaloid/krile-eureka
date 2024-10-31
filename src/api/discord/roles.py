from nullsafe import _
from api.api_webserver import ApiRequest
import bot


class DiscordRolesRequest(ApiRequest):
    """
    DiscordRolesRequest API

    Endpoint:
        GET /api/discord/roles

    Responses:
        200 OK:
        Description: Successfully retrieved the list of roles for each guild.
        Example:
            [
                {
                    "guild": 123456789012345678,
                    "roles": [
                        {
                            "id": 987654321098765432,
                            "name": "Admin"
                        },
                        {
                            "id": 876543210987654321,
                            "name": "Moderator"
                        }
                    ]
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
    def route(cls): return 'discord/roles'

    def get(self):
        """
        Retrieves the roles for each guild in the user's cache.

        Returns:
            tuple: A list of dictionaries containing guild IDs and their respective roles,
                   or an error message with a 401 status code if there is an error.
        """
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