

from data.table.definition import ColumnType, TableDefinition

class MissedData:
    guild: int
    user: int
    amount: int
    
    def __init__(self, guild: int, user: int, amount: int = 0): 
        self.guild = guild
        self.user = user
        self.amount = amount

class MissedTable(TableDefinition):
    def init_definitions(self):
        self.define_column('guild', ColumnType.BIGINT)
        self.define_column('user_id', ColumnType.BIGINT)
        self.define_column('amount', ColumnType.INTEGER)