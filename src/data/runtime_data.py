from datetime import datetime
import bot
import data.cache.message_cache as cache
from data.db.sql import Record
from data.eureka_info import EurekaInfo
from data.events.event_template import DefaultEventTemplates
from data.guilds.guild import Guilds
from data.db.register import RegisterTables
from data.db.definition import TableDefinitions
from data.tasks.tasks import TaskExecutionType, Tasks
from data.ui.ui import UI
from data.ui.copied_messages import MessageCopyController

class RuntimeData:
    """General Runtime Data Class"""
    message_copy_controller: MessageCopyController
    guilds: Guilds
    ui: UI
    tasks: Tasks
    eureka_info: EurekaInfo
    default_event_templates: DefaultEventTemplates
    ready: bool

    def __init__(self):
        self.default_event_templates = DefaultEventTemplates()
        self.guilds = Guilds(self.default_event_templates)
        self.ui = UI()
        self.tasks = Tasks()
        self.eureka_info = EurekaInfo()

        self.ready = False
        RegisterTables.register()
        self.ensure_database_tables()
        self.message_copy_controller = MessageCopyController()

    def ensure_database_tables(self):
        """Create the database and update the tables."""
        record = Record()
        for table in TableDefinitions.DEFINITIONS:
            record.DATABASE.query(table.to_sql_create())
            record.DATABASE.query(table.to_sql_alter())

    async def reset(self):
        """Load general data from the db."""
        if self.ready:
            self.__init__()
        await self.ui.load()
        self.guilds.load()
        self.tasks.load()
        self.eureka_info.load()
        self.ready = True
        cache.messages.cache.clear()
        for guild in bot.instance.guilds:
            await guild.fetch_members()
            await self.ui.schedule.rebuild(guild.id)

        if not self.tasks.contains(TaskExecutionType.UPDATE_STATUS):
            self.tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_STATUS)
        if not self.tasks.contains(TaskExecutionType.UPDATE_EUREKA_INFO_POSTS):
            self.tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_EUREKA_INFO_POSTS)