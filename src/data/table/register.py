from data.table.definition import TableDefinitions
from data.table.buttons import ButtonsTable
from data.table.guilds import GuildTable
from data.table.schedule import ScheduleTable

class RegisterTables:
    @classmethod
    def register(cls):
        TableDefinitions.register(ButtonsTable('buttons'))
        TableDefinitions.register(GuildTable('guilds'))
        TableDefinitions.register(ScheduleTable('schedule'))