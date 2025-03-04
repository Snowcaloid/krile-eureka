import asyncio

from centralized_data import Bindable
from discord import Intents
from discord.ext.commands import Bot as DiscordBot
from typing import Callable, Coroutine

class Bot(Bindable):
    """General bot class."""
    class _InnerClient(DiscordBot):
        def __init__(self):
            self.krile_setup_hook: Callable[[DiscordBot], Coroutine[None, None, None]] = None
            self.krile_reload_hook: Callable[[DiscordBot, bool], Coroutine[None, None, None]] = None
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
        self.client = Bot._InnerClient()