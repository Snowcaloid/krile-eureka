from data.db.definition import TableDefinition, ColumnType, ColumnFlag


class SignupSlotsTable(TableDefinition):
    def init_definitions(self):
        self.define_column('id', ColumnType.SERIAL, 0, [ColumnFlag.UNIQUE])
        self.define_column('signup_id', ColumnType.INTEGER)
        self.define_column('slot_id', ColumnType.INTEGER)
        self.define_column('user_id', ColumnType.BIGINT)
