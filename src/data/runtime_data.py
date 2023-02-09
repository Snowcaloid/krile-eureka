from typing import List
from data.role_post_data import RolePostData
from data.query import Query, QueryOwner, QueryType
from data.table.register import RegisterTables
from data.table.database import Database
from data.table.definition import TableDefinitions
from data.table.buttons import ButtonData
        
class RuntimeData(QueryOwner):
    _loaded_view: List[ButtonData] = []
    db: Database = None
    role_post_data: RolePostData = None
    query: Query = None
    
    def __init__(self):
        RegisterTables.register()
        self.db = Database()
        self.init_db()
        self.role_post_data = RolePostData()
        self.query          = Query(self)
        self.load_db_data()

    def finish_query(self, user: int, type: QueryType) -> None:
        if type == QueryType.ROLE_POST:
            self.role_post_data.save(self.db, user)
            self.role_post_data.clear(user)
    
    def init_db(self):
        self.db.connect()
        try:
            for table in TableDefinitions.DEFINITIONS:
                self.db.query(table.to_sql_create())
                self.db.query(table.to_sql_alter())
        finally:
            self.db.disconnect()
            
    def load_db_data(self):
        for record in self.db.query('select * from buttons'):
            self._loaded_view.append(ButtonData(record[0], record[1]))