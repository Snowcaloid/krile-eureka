from data.db.definition import ColumnFlag, ColumnType, TableDefinition

class GuildRolesTable(TableDefinition):
    def init_definitions(self):
        self.define_column('id', ColumnType.SERIAL, 0, [ColumnFlag.UNIQUE, ColumnFlag.PRIMARY_KEY])
        self.define_column('guild_id', ColumnType.BIGINT)
        self.define_column('role_id', ColumnType.BIGINT)
        self.define_column('event_category', ColumnType.VARCHAR, 15)
        self.define_column('function', ColumnType.INTEGER)