from datetime import datetime
from threading import Thread
from api.register_handlers import register_api_handlers
import bot
import data.cache.message_cache as cache
import api.api_webserver as ws
from data.db.sql import Record
from data.eureka_info import EurekaInfo
from data.guilds.guild import Guilds
from data.db.register import RegisterTables
from data.db.definition import TableDefinitions
from data.tasks.tasks import TaskExecutionType, Tasks
from data.ui.ui import UI
from data.ui.copied_messages import MessageCopyController

class RuntimeData:
    """General Runtime Data Class"""
    message_copy_controller: MessageCopyController
    guilds: Guilds = Guilds()
    ui: UI = UI()
    tasks: Tasks = Tasks()
    eureka_info: EurekaInfo = EurekaInfo()
    ready: bool
    thread = Thread(target=ws.run)

    def __init__(self):
        self.ready = False
        RegisterTables.register()
        self.ensure_database_tables()
        self.message_copy_controller = MessageCopyController()
        register_api_handlers()
        self.thread.start()

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