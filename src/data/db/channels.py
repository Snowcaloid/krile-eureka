from data.db.definition import TableDefinition, ColumnType, ColumnFlag

class ChannelTable(TableDefinition):
    def init_definitions(self):
        self.define_column('id', ColumnType.SERIAL, 0, [ColumnFlag.UNIQUE])
        self.define_column('guild_id', ColumnType.BIGINT)
        self.define_column('event_type', ColumnType.VARCHAR, 15)
        self.define_column('channel_id', ColumnType.BIGINT)
        self.define_column('function', ColumnType.INTEGER)