from datetime import datetime
import bot
from data.cache.message_cache import MessageCache
from data.db.sql import Record
from data.eureka_info import EurekaInfo
from data.guilds.guild import Guilds
from data.db.definition import TableDefinitions
from data.tasks.task import TaskExecutionType
from data.tasks.tasks import Tasks
from data.ui.ui import UI
from data.ui.copied_messages import MessageCopyController

class RuntimeData:
    """General Runtime Data Class"""
    message_copy_controller: MessageCopyController = MessageCopyController()
    guilds: Guilds
    ui: UI = UI()
    ready: bool

    @Tasks.bind
    def tasks(self) -> Tasks: ...

    @EurekaInfo.bind
    def eureka_info(self) -> EurekaInfo: ...

    @TableDefinitions.bind
    def tables(self) -> TableDefinitions: ...

    def __init__(self):
        self.ready = False
        self.guilds = Guilds()
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
        self.tasks.load()
        self.eureka_info.load()
        self.ready = True
        MessageCache().clear()
        for guild in bot.instance.guilds:
            await self.ui.schedule.rebuild(guild.id)

        if not self.tasks.contains(TaskExecutionType.UPDATE_STATUS):
            self.tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_STATUS)
        if not self.tasks.contains(TaskExecutionType.UPDATE_EUREKA_INFO_POSTS):
            self.tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_EUREKA_INFO_POSTS)