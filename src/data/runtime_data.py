from datetime import datetime
import bot
from data.cache.message_cache import MessageCache
from basic_types import TaskExecutionType
from data.events.schedule import Schedule
from data.guilds.guild_channel import GuildChannels
from data.ui.ui import UI

class RuntimeData:
    """General Runtime Data Class"""
    ui: UI = UI()
    ready: bool

    from data.tasks.tasks import Tasks
    @Tasks.bind
    def tasks(self) -> Tasks: ...

    from data.eureka_info import EurekaInfo
    @EurekaInfo.bind
    def eureka_info(self) -> EurekaInfo: ...

    from data.guilds.guild import Guilds
    @Guilds.bind
    def guilds(self) -> Guilds: ...

    def __init__(self):
        self.ready = False

    async def reset(self):
        """Load general data from the db."""
        if self.ready:
            self.ready = False
        await self.ui.load()
        self.guilds.load()
        for guild in bot.instance.guilds:
            Schedule(guild.id).load()
            GuildChannels(guild.id).load()
            await self.ui.schedule.rebuild(guild.id)
        self.eureka_info.load()
        self.tasks.load()
        self.ready = True
        MessageCache().clear()

        if not self.tasks.contains(TaskExecutionType.UPDATE_STATUS):
            self.tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_STATUS)
        if not self.tasks.contains(TaskExecutionType.UPDATE_EUREKA_INFO_POSTS):
            self.tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_EUREKA_INFO_POSTS)