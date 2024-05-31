from data.db.definition import TableDefinition, ColumnType, ColumnFlag

class ButtonsTable(TableDefinition):
    def init_definitions(self):
        self.define_column('button_id', ColumnType.VARCHAR, 50, [ColumnFlag.UNIQUE, ColumnFlag.PRIMARY_KEY])
        self.define_column('button_type', ColumnType.INTEGER)
        self.define_column('channel_id', ColumnType.BIGINT)
        self.define_column('message_id', ColumnType.BIGINT)
        self.define_column('emoji', ColumnType.VARCHAR, 2)
        self.define_column('label', ColumnType.VARCHAR, 50)
        self.define_column('style', ColumnType.INTEGER)
        self.define_column('row', ColumnType.INTEGER)
        self.define_column('index', ColumnType.INTEGER)
        self.define_column('role', ColumnType.BIGINT)
        self.define_column('pl', ColumnType.INTEGER)