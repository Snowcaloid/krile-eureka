from data.db.definition import TableDefinition, ColumnType, ColumnFlag, ColumnDefinition
from typing import List


class EventsTable(TableDefinition):
    _columns: List[ColumnDefinition] = []
    def init_definitions(self):
        self.define_column('id', ColumnType.SERIAL, 0, [ColumnFlag.PRIMARY_KEY])
        self.define_column('guild_id', ColumnType.BIGINT)
        self.define_column('event_type', ColumnType.VARCHAR, 15)
        self.define_column('timestamp', ColumnType.TIMESTAMP)
        self.define_column('description', ColumnType.TEXT)
        self.define_column('raid_leader', ColumnType.BIGINT)
        self.define_column('pl1', ColumnType.BIGINT)
        self.define_column('pl2', ColumnType.BIGINT)
        self.define_column('pl3', ColumnType.BIGINT)
        self.define_column('pl4', ColumnType.BIGINT)
        self.define_column('pl5', ColumnType.BIGINT)
        self.define_column('pl6', ColumnType.BIGINT)
        self.define_column('pls', ColumnType.BIGINT)
        self.define_column('use_support', ColumnType.BOOLEAN)
        self.define_column('pass_main', ColumnType.INTEGER)
        self.define_column('pass_supp', ColumnType.INTEGER)
        self.define_column('pl_post_id', ColumnType.BIGINT)
        self.define_column('finished', ColumnType.BOOLEAN)
        self.define_column('canceled', ColumnType.BOOLEAN)
