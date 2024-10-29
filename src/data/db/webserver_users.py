from data.db.definition import TableDefinition, ColumnType, ColumnFlag

class WebserverUsersTable(TableDefinition):
    def init_definitions(self):
        self.define_column('uuid', ColumnType.VARCHAR, 36, [ColumnFlag.UNIQUE])
        self.define_column('user_id', ColumnType.BIGINT)
        self.define_column('user_name', ColumnType.VARCHAR, 50)