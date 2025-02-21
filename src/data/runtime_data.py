from datetime import datetime
import bot
from data.cache.message_cache import MessageCache
from data.db.sql import Record
from basic_types import TaskExecutionType
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

    from data.db.definition import TableDefinitions
    @TableDefinitions.bind
    def tables(self) -> TableDefinitions: ...

    from data.guilds.guild import Guilds
    @Guilds.bind
    def guilds(self) -> Guilds: ...

    from data.events.schedule import Schedule
    @Schedule.bind
    def schedule(self) -> Schedule: ...

    def __init__(self):
        self.ready = False
        self.ensure_database_tables()

    def ensure_database_tables(self):
        """Create the database and update the tables."""
        record = Record()
        for table in self.tables.loaded_assets:
            record.DATABASE.query(table.to_sql_create())
            record.DATABASE.query(table.to_sql_alter())

    async def reset(self):
        """Load general data from the db."""
        if self.ready:
            self.ready = False
        await self.ui.load()
        self.guilds.load()
        self.schedule.load()
        self.eureka_info.load()
        self.tasks.load()
        self.ready = True
        MessageCache().clear()
        for guild in bot.instance.guilds:
            await self.ui.schedule.rebuild(guild.id)

        if not self.tasks.contains(TaskExecutionType.UPDATE_STATUS):
            self.tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_STATUS)
        if not self.tasks.contains(TaskExecutionType.UPDATE_EUREKA_INFO_POSTS):
            self.tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_EUREKA_INFO_POSTS)