import bot
from data.ui.embeds import EmbedController
from data.guilds.guild import Guilds
from data.runtime_processes import RunTimeProccesses, ProcessListener, RunTimeProcessType
from data.db.register import RegisterTables
from data.db.database import Database
from data.db.definition import TableDefinitions
from data.tasks.tasks import Tasks
from data.ui.ui import UI
from data.ui.copied_messages import MessageCopyController

class RuntimeData(ProcessListener):
    """General Runtime Data Class"""
    db: Database = Database()
    embed_controller: EmbedController
    message_copy_controller: MessageCopyController
    guilds: Guilds = Guilds()
    ui: UI = UI()
    tasks: Tasks = Tasks()
    processes: RunTimeProccesses
    ready: bool

    def __init__(self):
        self.ready = False
        RegisterTables.register()
        self.ensure_database_tables()
        self.processes = RunTimeProccesses(self)
        self.embed_controller = EmbedController()
        self.message_copy_controller = MessageCopyController()

    def on_finish_process(self, user: int, type: RunTimeProcessType) -> None:
        if type == RunTimeProcessType.EMBED_CREATION:
            self.embed_controller.clear(user)

    def ensure_database_tables(self):
        """Create the database and update the tables."""
        self.db.connect()
        try:
            for table in TableDefinitions.DEFINITIONS:
                self.db.query(table.to_sql_create())
                self.db.query(table.to_sql_alter())
        finally:
            self.db.disconnect()

    async def reset(self):
        """Load general data from the db."""
        if self.ready:
            self.__init__()
        self.ui.load()
        self.guilds.load()
        self.tasks.load()
        self.ready = True
        for guild in bot.instance.guilds:
            guild.fetch_members()
            await self.ui.schedule.rebuild(guild.id)