from data.table.channels import ChannelTable
from data.table.definition import TableDefinitions
from data.table.buttons import ButtonsTable
from data.table.guilds import GuildTable
from data.table.missed import MissedTable
from data.table.pings import PingsTable
from data.table.schedule import ScheduleTable
from data.table.tasks import TaskTable

class RegisterTables:
    @classmethod
    def register(cls):
        TableDefinitions.register(ButtonsTable('buttons'))
        TableDefinitions.register(GuildTable('guilds'))
        TableDefinitions.register(ChannelTable('channels'))
        TableDefinitions.register(ScheduleTable('schedule'))
        TableDefinitions.register(TaskTable('tasks'))
        TableDefinitions.register(MissedTable('missed'))
        TableDefinitions.register(PingsTable('pings'))
