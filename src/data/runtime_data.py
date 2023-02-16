from datetime import datetime
from typing import List
import bot as runtime_data_bot
from data.role_post_data import RolePostData
from data.schedule_post_data import SchedulePostData
from data.query import Query, QueryOwner, QueryType
from data.table.register import RegisterTables
from data.table.database import Database
from data.table.definition import TableDefinitions
from data.table.buttons import ButtonData
from discord.ext.commands import Bot
from data.runtime_guild_data import RuntimeGuildData
from data.table.tasks import TaskExecutionType
from data.task_list import TaskList
        
class RuntimeData(QueryOwner):
    _loaded_view: List[ButtonData]
    db: Database
    role_posts: RolePostData
    schedule_posts: SchedulePostData
    guild_data: RuntimeGuildData
    tasks: TaskList
    query: Query
    ready: bool
    
    def __init__(self):
        self.ready = False
        RegisterTables.register()
        self._loaded_view = []
        self.db = Database()
        self.init_db()
        self.role_posts     = RolePostData()
        self.guild_data     = RuntimeGuildData()
        self.tasks          = TaskList()
        self.schedule_posts = SchedulePostData(self.guild_data)
        self.query          = Query(self)

    def finish_query(self, user: int, type: QueryType) -> None:
        if type == QueryType.ROLE_POST:
            self.role_posts.save(self.db, user)
            self.role_posts.clear(user)
    
    def init_db(self):
        self.db.connect()
        try:
            for table in TableDefinitions.DEFINITIONS:
                self.db.query(table.to_sql_create())
                self.db.query(table.to_sql_alter())
        finally:
            self.db.disconnect()
            
    def load_db_view(self):
        for record in self.db.query('select * from buttons'):
            self._loaded_view.append(ButtonData(record[0], record[1]))
            
    async def load_db_data(self):
        self.guild_data.load(self.db)
        for data in self.guild_data._list:
            for guild in runtime_data_bot.snowcaloid.guilds:
                if data.guild_id == guild.id:
                    guild.fetch_members()
        await self.schedule_posts.load(self.db)
        self.tasks.load()
        self.ready = True
        self.tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_STATUS) 