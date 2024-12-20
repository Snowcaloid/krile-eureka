from data.db.definition import TableDefinition, ColumnType, ColumnFlag


class GuildTable(TableDefinition):
    def init_definitions(self):
        self.define_column('guild_id', ColumnType.BIGINT, 0, [ColumnFlag.UNIQUE, ColumnFlag.PRIMARY_KEY])
        self.define_column('role_developer', ColumnType.BIGINT)
        self.define_column('role_admin', ColumnType.BIGINT)
