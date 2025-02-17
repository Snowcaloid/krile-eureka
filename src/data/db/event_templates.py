from data.db.definition import TableDefinition, ColumnType, ColumnFlag, ColumnDefinition
from typing import List


class EventTemplatesTable(TableDefinition):
    _columns: List[ColumnDefinition] = []
    def init_definitions(self):
        self.define_column('guild_id', ColumnType.BIGINT)
        self.define_column('event_type', ColumnType.VARCHAR, 15, [ColumnFlag.PRIMARY_KEY])
        self.define_column('data', ColumnType.JSON)