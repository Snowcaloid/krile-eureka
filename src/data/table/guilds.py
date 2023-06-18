from data.table.channels import ChannelData, InfoTitleType
from data.table.definition import TableDefinition, ColumnType, ColumnFlag
from typing import List

from data.table.schedule import ScheduleType


class GuildData:
    guild_id: int
    schedule_channel: int
    schedule_post: int
    missed_channel: int
    missed_post: int
    missed_role: str
    log_channel: int
    _channels: List[ChannelData]

    def __init__(self, guild_id: int, schedule_channel: int, schedule_post: int, missed_channel: int, missed_post: int, log_channel: int, missed_role: str = ''):
        self.guild_id = guild_id
        self.schedule_channel = schedule_channel
        self.schedule_post = schedule_post
        self.missed_channel = missed_channel
        self.missed_post = missed_post
        self.missed_role = missed_role
        self.log_channel = log_channel
        self._channels = []

    def get_channel(self, channel_id: int = 0, type: ScheduleType = '', info_title_type: InfoTitleType = InfoTitleType.NONE) -> ChannelData:
        if channel_id:
            for ch in self._channels:
                if ch.channel_id == channel_id and not ch.is_pl_channel and not ch.is_support_channel:
                    return ch
        if type:
            for ch in self._channels:
                if ch.guild_id == self.guild_id and ch.type == type and not ch.is_pl_channel and not ch.is_support_channel:
                    return ch
        if info_title_type:
            for ch in self._channels:
                if ch.guild_id == self.guild_id and ch.info_title_type == info_title_type.value:
                    return ch
        ch = ChannelData(self.guild_id, '', channel_id)
        self._channels.append(ch)
        return ch

    def get_pl_channel(self, type: ScheduleType) -> ChannelData:
        for ch in self._channels:
            if ch.guild_id == self.guild_id and ch.type == type and ch.is_pl_channel:
                return ch
        return None

    def get_support_channel(self, type: ScheduleType) -> ChannelData:
        for ch in self._channels:
            if ch.guild_id == self.guild_id and ch.type == type and ch.is_support_channel:
                return ch
        return None

    def remove_channel(self, channel_id: int = 0, type: ScheduleType = '', info_title_type: InfoTitleType = InfoTitleType.NONE):
        self._channels.remove(self.get_channel(channel_id, type, info_title_type))

    def add_channel(self, channel_id: int, type: ScheduleType, is_pl_channel: bool = False, is_support_channel: bool = False):
        self._channels.append(ChannelData(self.guild_id, type, channel_id, is_pl_channel, is_support_channel))

    def add_info_channel(self, channel_id: int, type: InfoTitleType):
        self._channels.append(ChannelData(self.guild_id, '', channel_id, False, False, type))

class GuildTable(TableDefinition):
    def init_definitions(self):
        self.define_column('guild_id', ColumnType.BIGINT, 0, [ColumnFlag.UNIQUE, ColumnFlag.PRIMARY_KEY])
        self.define_column('schedule_channel', ColumnType.BIGINT)
        self.define_column('schedule_post', ColumnType.BIGINT)
        self.define_column('missed_channel', ColumnType.BIGINT)
        self.define_column('missed_post', ColumnType.BIGINT)
        self.define_column('missed_role', ColumnType.BIGINT)
        self.define_column('log_channel', ColumnType.BIGINT)
