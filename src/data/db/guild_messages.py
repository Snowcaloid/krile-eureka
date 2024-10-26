from data.db.definition import ColumnFlag, ColumnType, TableDefinition

class GuildMessagesTable(TableDefinition):
    def init_definitions(self):
        self.define_column('id', ColumnType.SERIAL, 0, [ColumnFlag.UNIQUE, ColumnFlag.PRIMARY_KEY])
        self.define_column('guild_id', ColumnType.BIGINT)
        self.define_column('channel_id', ColumnType.BIGINT)
        self.define_column('message_id', ColumnType.BIGINT)
        self.define_column('function', ColumnType.INTEGER)
        self.define_column('event_type', ColumnType.VARCHAR, 15)