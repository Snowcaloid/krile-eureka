from abc import ABC, abstractmethod
import os
from datetime import datetime
from typing import Optional

from centralized_data import GlobalCollection
from discord import Guild, Interaction, TextChannel
from models.channel_assignment import ChannelAssignmentStruct
from utils.basic_types import GuildID, ChannelFunction
from utils.functions import default_response, get_discord_timestamp

class BaseLogger(ABC):
    def format_timestamp(self, timestamp: datetime) -> str:
        """Format a timestamp for logging."""
        return timestamp.strftime('[%Y-%m-%d %H:%M:%S]')

    @abstractmethod
    def log(self, message: str) -> None: ...

    def flush(self, message: str, exc_type: Optional[type] = None) -> None:
        self.log(message)


class ConsoleLogger(BaseLogger):
    def log(self, message: str) -> None:
        """
        Log a message to the console.
        This log is accessible when debugging or running the bot in docker.
        """
        print(f'{self.format_timestamp(datetime.utcnow())} {message}')


class FileLogger(BaseLogger):
    def __init__(self, guild_id: Optional[int] = None):
        self.file_path = datetime.now().strftime(os.getenv('LOG_FILE_PATH', './logs/bot.log'))
        self.file_path = self.file_path.replace('{guild_id}', str(guild_id) if guild_id else '000000000000000000')
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def log(self, message: str) -> None:
        """
        Log a message to a file.
        This log is accessible when debugging or running the bot in docker.
        """
        with open(self.file_path, 'a') as file:
            file.write(f'{self.format_timestamp(datetime.now())} {message}\n')


async def _guild_respond(interaction: Interaction, message: str, guild: Guild):
    if hasattr(interaction, 'response'):
        await default_response(interaction, f'{message}')
    from data_providers.channel_assignments import ChannelAssignmentProvider

    assert interaction.guild_id is not None, "Guild Interaction must have a guild ID"

    channel = ChannelAssignmentProvider().find(ChannelAssignmentStruct(
        guild_id=interaction.guild_id,
        function=ChannelFunction.LOGGING
    ))
    if channel is None: return
    channel = guild.get_channel(channel.channel_id)
    if not isinstance(channel, TextChannel): return
    await channel.send(f'{get_discord_timestamp(datetime.utcnow())} {message}')


class GuildLogger(GlobalCollection[GuildID], BaseLogger):
    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    def constructor(self, guild_id: GuildID):
        super().__init__(guild_id)
        self.console_logger = ConsoleLogger()
        self.file_logger = FileLogger(guild_id)
        self.guild = self._bot._client.get_guild(guild_id)

    def log(self, message: str) -> None:
        """
        Log a message to the guild's log channel and to a file.
        This log is accessible when debugging or running the bot in docker.
        """
        self.console_logger.log(message)
        self.file_logger.log(message)

    def respond(self, interaction: Interaction, message: str) -> None:
        from tasks import Tasks
        Tasks.run_async_method(_guild_respond, *[interaction, message, self.guild])
