import asyncio
from types import CoroutineType

from centralized_data import Bindable
from discord import Guild, Intents, Member, Role, TextChannel, User
from discord.ext.commands import Bot as DiscordBot
from typing import Any, Callable, Sequence

class Bot(Bindable):
    """General bot class."""
    class _InnerClient(DiscordBot):
        def __init__(self):
            self.krile_setup_hook: Callable[[DiscordBot], CoroutineType[Any, Any, None]]
            self.krile_reload_hook: Callable[[DiscordBot, bool], CoroutineType[Any, Any, None]]
            intents = Intents.all()
            intents.message_content = True
            intents.emojis = True
            intents.emojis_and_stickers = True
            intents.members = True
            super().__init__(command_prefix='/', intents=intents)

        async def reload_data_classes(self, initial: bool = False):
            while self.krile_reload_hook == None:
                await asyncio.sleep(1)

            await self.krile_reload_hook(self, initial)

        async def setup_hook(self) -> None:
            """A coroutine to be called to setup the bot.
            This method is called after instance.on_ready event.
            """
            while self.krile_setup_hook == None:
                await asyncio.sleep(1)

            await self.krile_setup_hook(self)

    def constructor(self):
        super().constructor()
        self._client = Bot._InnerClient()

    def get_guild(self, guild_id: Any) -> Guild:
        """Get a guild by its ID, assuming it exists."""
        return self._client.get_guild(guild_id) #type: ignore seriously...

    def get_text_channel(self, channel_id: Any) -> TextChannel:
        """Get a text channel by its ID."""
        channel = self._client.get_channel(channel_id)
        assert isinstance(channel, TextChannel), f'expected TextChannel, got {channel.__class__.__name__}'
        return channel

    def get_user(self, user_id: Any) -> Member:
        """Get a user by its ID, assuming it exists."""
        return self._client.get_user(user_id) #type: ignore seriously...

    def get_member(self, guild_id: Any, member_id: Any) -> Member:
        """Get a member by its ID in a specific guild, assuming it exists."""
        return self.get_guild(guild_id).get_member(member_id) #type: ignore seriously...

    def get_role(self, guild_id: Any, role_id: Any) -> Role:
        """Get a role by its ID in a specific guild, assuming it exists."""
        return self.get_guild(guild_id).get_role(role_id) #type: ignore seriously...

    @property
    def guilds(self) -> Sequence[Guild]:
        """Get a list of all guilds the bot is in."""
        return self._client.guilds

    @property
    def user(self) -> User:
        """Get the bot's user object."""
        return self._client.user # type: ignore seriously...