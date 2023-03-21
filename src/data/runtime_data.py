from typing import List
import bot
from data.embed_data import EmbedData
from data.missed_runs_data import MissedRunsData
from data.schedule_post_data import SchedulePostData
from data.query import Query, QueryOwner, QueryType
from data.table.register import RegisterTables
from data.table.database import Database
from data.table.definition import TableDefinitions
from data.table.buttons import ButtonData
from data.runtime_guild_data import RuntimeGuildData
from data.task_list import TaskList

class RuntimeData(QueryOwner):
    """General Runtime Data Class

    Properties
    ----------
    _loaded_view: :class:`List[ButtonData]`
        A list of buttons, that are loaded upon starting the application,
        used to restore functionality of buttons upon logging in.
    db: :class:`Database`
        Database access. connect -> query -> disconnect
    embeds: :class:`EmbedData`
        Runtime data which stores entries for an embed during a user query.
        It is created with command /embed create, and is emptied upon
        using /embed finish.
    schedule_posts: :class:`SchedulePostData`
        Runtime data which stores a list of Schedule posts and the entries within them.
        This object has all the functionality regarding scheduling, including setting
        schedule channels, etc.
    guild_data: :class:`RuntimeGuildData`
        Runtime data which stores base properties of a guild, e.g which event type
        should be posted in which channel.
    tasks: :class:`TaskList`
        Runtime data which contains the tasks, which are fired by the main task loop
        in src/tasks.py.
    query: :class:`Query`
        Interactive query data. Currently only used in /embed commands.
    ready: :class:`bool`
        Returns True whenever all data has been loaded from the database and is ready
        to be used.
    """
    _loaded_view: List[ButtonData]
    db: Database
    embeds: EmbedData
    schedule_posts: SchedulePostData
    guild_data: RuntimeGuildData
    missed_runs: MissedRunsData
    tasks: TaskList
    query: Query
    ready: bool

    def __init__(self):
        self.ready = False
        RegisterTables.register()
        self._loaded_view = []
        self.db = Database()
        self.init_db()
        self.embeds         = EmbedData()
        self.guild_data     = RuntimeGuildData()
        self.missed_runs    = MissedRunsData()
        self.schedule_posts = SchedulePostData(self.guild_data)
        self.tasks          = TaskList()
        self.query          = Query(self)

    def finish_query(self, user: int, type: QueryType) -> None:
        """What happens when a user query is finished

        Args:
            user (int): user id, whose query is done
            type (QueryType): which query type has been finished
        """
        if type == QueryType.EMBED:
            self.embeds.save(user)
            self.embeds.clear(user)

    def init_db(self):
        """Create the database and update the tables."""
        self.db.connect()
        try:
            for table in TableDefinitions.DEFINITIONS:
                self.db.query(table.to_sql_create())
                self.db.query(table.to_sql_alter())
        finally:
            self.db.disconnect()

    def load_db_view(self):
        """Load buttons to be restored."""
        for record in self.db.query('select * from buttons'):
            self._loaded_view.append(ButtonData(record[0], record[1]))

    async def load_db_data(self):
        """Load general data from the db."""
        if self.ready:
            self.__init__()
        self.guild_data.load()
        for data in self.guild_data._list:
            for guild in bot.krile.guilds:
                if data.guild_id == guild.id:
                    guild.fetch_members()
        await self.schedule_posts.load()
        await self.missed_runs.load()
        self.tasks.load()
        self.ready = True