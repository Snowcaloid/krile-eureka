from discord import ChannelType
from nullsafe import _
from api.api_webserver import ApiRequest
import bot


class DiscordChannelsRequest(ApiRequest):
    """
    DiscordChannelsRequest API

    Endpoint:
        GET /api/discord/channels

    Responses:
        200 OK:
        Description: Successfully retrieved the list of text channels.
        Example:
            [
                {
                    "guild": 123456789012345678,
                    "channels": [
                        {
                            "id": 987654321098765432,
                            "name": "general"
                        },
                        {
                            "id": 876543210987654321,
                            "name": "random"
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
    def route(cls): return 'discord/channels'

    def get(self):
        """
        Retrieves the list of text channels for each guild in the user's cache.

        Returns:
            tuple: A tuple containing an error message and status code (401) if there is an error retrieving the user cache.
            list: A list of dictionaries, each containing a guild ID and a list of its text channels. Each channel is represented by a dictionary with its ID and name.
        """
        user_cache, error = self.get_user_cache()
        if error: return error, 401
        result = []
        for cached_guild in user_cache.guilds:
            data = {'guild': cached_guild['id'], 'channels': []}
            result.append(data)
            guild = bot.instance.get_guild(cached_guild['id'])
            for channel in guild.channels:
                if channel.type == ChannelType.text:
                    data['channels'].append({
                        'id': channel.id,
                        'name': channel.name})
        return result