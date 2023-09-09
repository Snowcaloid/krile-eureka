from data.db.definition import TableDefinition, ColumnType, ColumnFlag


class PingsTable(TableDefinition):
    def init_definitions(self):
        self.define_column('id', ColumnType.SERIAL, 0, [ColumnFlag.UNIQUE])
        self.define_column('guild_id', ColumnType.BIGINT)
        self.define_column('ping_type', ColumnType.INTEGER)
        self.define_column('schedule_type', ColumnType.VARCHAR, 15)
        self.define_column('tag', ColumnType.BIGINT)
