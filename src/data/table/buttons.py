from data.table.definition import TableDefinition, ColumnType, ColumnFlag

class ButtonData:
    button_id: str
    label: str
    
    def __init__(self, button_id: str, label: str = ''):
        self.button_id = button_id
        self.label = label
    
class ButtonsTable(TableDefinition):
    def init_definitions(self):
        self.define_column('button_id', ColumnType.VARCHAR, 50, [ColumnFlag.UNIQUE, ColumnFlag.PRIMARY_KEY])
        self.define_column('label', ColumnType.VARCHAR, 50)