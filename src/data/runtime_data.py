from typing import List
from data.role_post_data import RolePostData
from data.schedule_post_data import SchedulePostData
from data.query import Query, QueryOwner, QueryType
from data.table.register import RegisterTables
from data.table.database import Database
from data.table.definition import TableDefinitions
from data.table.buttons import ButtonData
from discord.ext.commands import Bot
from data.runtime_guild_data import RuntimeGuildData
        
class RuntimeData(QueryOwner):
    _loaded_view: List[ButtonData]
    db: Database
    role_posts: RolePostData
    schedule_posts: SchedulePostData
    guild_data: RuntimeGuildData
    query: Query
    
    def __init__(self):
        RegisterTables.register()
        self._loaded_view = []
        self.db = Database()
        self.init_db()
        self.role_posts     = RolePostData()
        self.guild_data     = RuntimeGuildData()
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
            
    async def load_db_data(self, bot: Bot):
        self.guild_data.load(self.db)
        await self.schedule_posts.load(bot, self.db)
        for record in self.db.query('select * from buttons'):
            self._loaded_view.append(ButtonData(record[0], record[1]))