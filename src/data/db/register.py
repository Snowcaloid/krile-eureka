from data.db.channels import ChannelTable
from data.db.definition import TableDefinitions
from data.db.buttons import ButtonsTable
from data.db.guild_messages import GuildMessagesTable
from data.db.guild_roles import GuildRolesTable
from data.db.guilds import GuildTable
from data.db.missed_records import MissedRecordsTable
from data.db.pings import PingsTable
from data.db.events import EventsTable
from data.db.tasks import TaskTable
from data.db.trackers import TrackersTable

class RegisterTables:
    @classmethod
    def register(cls):
        TableDefinitions.clear()
        TableDefinitions.register(ButtonsTable('buttons'))
        TableDefinitions.register(GuildTable('guilds'))
        TableDefinitions.register(ChannelTable('channels'))
        TableDefinitions.register(EventsTable('events'))
        TableDefinitions.register(TaskTable('tasks'))
        TableDefinitions.register(MissedRecordsTable('missed_records'))
        TableDefinitions.register(PingsTable('pings'))
        TableDefinitions.register(GuildRolesTable('guild_roles'))
        TableDefinitions.register(GuildMessagesTable('guild_messages'))
        TableDefinitions.register(TrackersTable('trackers'))
