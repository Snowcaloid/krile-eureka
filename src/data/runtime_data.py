from datetime import datetime
import bot
from data.cache.message_cache import MessageCache
from basic_types import TaskExecutionType
from data.events.schedule import Schedule
from data.guilds.guild_channel import GuildChannels
from data.guilds.guild_messages import GuildMessages
from data.guilds.guild_pings import GuildPings
from data.guilds.guild_roles import GuildRoles

class RuntimeData:
    """General Runtime Data Class"""
    from data.tasks.tasks import Tasks
    @Tasks.bind
    def tasks(self) -> Tasks: ...

    from data.eureka_info import EurekaInfo
    @EurekaInfo.bind
    def eureka_info(self) -> EurekaInfo: ...

    from data.ui.button_loader import ButtonLoader
    @ButtonLoader.bind
    def button_loader(self) -> ButtonLoader: ...

    async def reset(self):
        """Load general data from the db."""
        await self.button_loader.load()
        # TODO: move, so that load() isnt ran twice the first time around
        self.eureka_info.load()
        MessageCache().clear()
        for guild in bot.instance.guilds:
            Schedule(guild.id).load()
            GuildChannels(guild.id).load()
            GuildMessages(guild.id).load()
            GuildRoles(guild.id).load()
            GuildPings(guild.id).load()
            await self.ui.schedule.rebuild(guild.id)

        self.tasks.load()

        if not self.tasks.contains(TaskExecutionType.UPDATE_STATUS):
            self.tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_STATUS)
        if not self.tasks.contains(TaskExecutionType.UPDATE_EUREKA_INFO_POSTS):
            self.tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_EUREKA_INFO_POSTS)