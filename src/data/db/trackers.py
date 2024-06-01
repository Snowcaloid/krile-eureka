from data.db.definition import TableDefinition, ColumnType


class TrackersTable(TableDefinition):
    def init_definitions(self):
        self.define_column('url', ColumnType.VARCHAR, 35)
        self.define_column('timestamp', ColumnType.TIMESTAMP)
        self.define_column('zone', ColumnType.INTEGER)
