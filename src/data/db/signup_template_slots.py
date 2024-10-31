from data.db.definition import TableDefinition, ColumnType, ColumnFlag


class SignupTemplateSlotsTable(TableDefinition):
    def init_definitions(self):
        self.define_column('id', ColumnType.SERIAL, 0, [ColumnFlag.UNIQUE])
        self.define_column('template_id', ColumnType.INTEGER)
        self.define_column('name', ColumnType.VARCHAR, 50)
        self.define_column('party', ColumnType.INTEGER)
        self.define_column('position', ColumnType.INTEGER)
