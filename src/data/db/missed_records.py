

from data.db.definition import ColumnType, TableDefinition

class MissedRecordsTable(TableDefinition):
    def init_definitions(self):
        self.define_column('guild_id', ColumnType.BIGINT)
        self.define_column('event_type', ColumnType.VARCHAR, 15)
        self.define_column('user_id', ColumnType.BIGINT)
        self.define_column('amount', ColumnType.INTEGER)