from data.table.definition import TableDefinition, ColumnType, ColumnFlag
from data.table.schedule import ScheduleType
from enum import Enum

class InfoTitleType(Enum):
    NONE = 0
    NEXT_RUN_TYPE = 1
    NEXT_RUN_START_TIME = 2
    NEXT_RUN_PASSCODE_TIME = 3

class ChannelData:
    guild_id: int
    type: ScheduleType
    channel_id: int
    is_pl_channel: bool
    is_support_channel: bool
    info_title_type: InfoTitleType

    def __init__(self, guild_id: int, type: ScheduleType, channel_id: int, is_pl_channel: bool = False, is_support_channel: bool = False,
                 info_title_type: InfoTitleType = InfoTitleType.NONE):
        self.guild_id = guild_id
        self.type = type
        self.channel_id = channel_id
        self.is_pl_channel = is_pl_channel
        self.is_support_channel = is_support_channel
        self.info_title_type = info_title_type

class ChannelTable(TableDefinition):
    def init_definitions(self):
        self.define_column('id', ColumnType.SERIAL, 0, [ColumnFlag.UNIQUE])
        self.define_column('guild_id', ColumnType.BIGINT)
        self.define_column('type', ColumnType.VARCHAR, 15)
        self.define_column('channel_id', ColumnType.BIGINT)
        self.define_column('is_pl_channel', ColumnType.BOOLEAN)
        self.define_column('is_support_channel', ColumnType.BOOLEAN)
        self.define_column('info_title_type', ColumnType.INTEGER)