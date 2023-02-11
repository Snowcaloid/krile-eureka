from data.table.definition import TableDefinition, ColumnType, ColumnFlag
from data.table.schedule import ScheduleType

class ChannelData:
    guild_id: int
    type: ScheduleType
    channel_id: int
    
    def __init__(self, guild_id: int, type: ScheduleType, channel_id: int):
        self.guild_id = guild_id
        self.type = type
        self.channel_id = channel_id
    
class ChannelTable(TableDefinition):
    def init_definitions(self):
        self.define_field('id', ColumnType.SERIAL, 0, [ColumnFlag.UNIQUE])
        self.define_field('guild_id', ColumnType.BIGINT)
        self.define_field('type', ColumnType.VARCHAR, 15)
        self.define_field('channel_id', ColumnType.BIGINT)