from typing import Union
from discord import Interaction, InteractionResponse
from bot import DiscordClient

class API_Interaction:
    @DiscordClient.bind
    def _client(self) -> DiscordClient: ...

    def __init__(self, user_id: int, guild_id: int) -> None:
        self.guild = self._client.get_guild(guild_id)
        self.guild_id = guild_id
        if self.guild is None: return
        self.user = self.guild.get_member(user_id)

InteractionLike = Union[Interaction, InteractionResponse, API_Interaction]