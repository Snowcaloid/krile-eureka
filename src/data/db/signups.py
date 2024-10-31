from data.db.definition import TableDefinition, ColumnType, ColumnFlag


class SignupsTable(TableDefinition):
    def init_definitions(self):
        self.define_column('id', ColumnType.SERIAL, 0, [ColumnFlag.UNIQUE])
        self.define_column('template_id', ColumnType.INTEGER)
