from data.db.definition import TableDefinition, ColumnType

class TaskTable(TableDefinition):
    def init_definitions(self):
        self.define_column('id', ColumnType.SERIAL)
        self.define_column('execution_time', ColumnType.TIMESTAMP)
        self.define_column('task_type', ColumnType.INTEGER)
        self.define_column('description', ColumnType.VARCHAR, 30)
        self.define_column('data', ColumnType.JSON)