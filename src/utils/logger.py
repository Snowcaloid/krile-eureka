from abc import ABC, abstractmethod
import os
from datetime import datetime
from typing import Coroutine

from centralized_data import GlobalCollection
from discord import Guild, Interaction
from utils.basic_types import GuildID, GuildChannelFunction, TaskExecutionType
from bot import Bot
from utils.functions import default_response, get_discord_timestamp

class BaseLogger(ABC):
    def format_timestamp(self, timestamp: datetime) -> str:
        """Format a timestamp for logging."""
        return timestamp.strftime('[%Y-%m-%d %H:%M:%S]')

    @abstractmethod
    def log(self, message: str) -> None: ...
    def flush(self, message: str, exc_type: type = None) -> None:
        self.log(message)


class ConsoleLogger(BaseLogger):
    def log(self, message: str) -> None:
        """
        Log a message to the console.
        This log is accessible when debugging or running the bot in docker.
        """
        print(f'{self.format_timestamp(datetime.utcnow())} {message}')


class FileLogger(BaseLogger):
    def __init__(self, guild_id: int = None):
        file_path = datetime.now().strftime(os.getenv('LOG_FILE_PATH', './logs/bot.log'))
        file_path = file_path.replace('{guild_id}', str(guild_id) if guild_id else '000000000000000000')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

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
    from data.services.channels_service import ChannelsService, ChannelStruct
    channel = ChannelsService(interaction.guild_id).find(ChannelStruct(
        guild_id=interaction.guild_id,
        function=GuildChannelFunction.LOGGING
    ))
    if channel is None: return
    channel = guild.get_channel(channel.channel_id)
    if channel is None: return
    await channel.send(f'{get_discord_timestamp(datetime.utcnow())} {message}')


class GuildLogger(GlobalCollection[GuildID], BaseLogger):
    from data.tasks.tasks import Tasks
    @Tasks.bind
    def tasks(self) -> 'Tasks': ...

    from bot import Bot
    @Bot.bind
    def bot(self) -> 'Bot': ...

    def constructor(self, guild_id: GuildID):
        super().__init__(guild_id)
        self.console_logger = ConsoleLogger()
        self.file_logger = FileLogger(guild_id)
        self.guild = self.bot.client.get_guild(guild_id)

    def log(self, message: str) -> None:
        """
        Log a message to the guild's log channel and to a file.
        This log is accessible when debugging or running the bot in docker.
        """
        self.console_logger.log(message)
        self.file_logger.log(message)

    def respond(self, interaction: Interaction, message: str) -> Coroutine[None, None, None]:
        self.tasks.add_task(
            datetime.utcnow(),
            TaskExecutionType.RUN_ASYNC_METHOD,
            {
                "method": _guild_respond,
                "args": [interaction, message, self.guild]
            }
