from data.table.definition import TableDefinitions
from data.table.buttons import ButtonsTable
from data.table.guilds import GuildTable

class RegisterTables:
    @classmethod
    def register(cls):
        TableDefinitions.register(ButtonsTable('buttons'))
        TableDefinitions.register(GuildTable('guilds'))