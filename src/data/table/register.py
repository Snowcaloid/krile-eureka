from data.table.buttons import ButtonsTable
from data.table.definition import TableDefinitions

class RegisterTables:
    @classmethod
    def register(cls):
        TableDefinitions.register(ButtonsTable('buttons'))