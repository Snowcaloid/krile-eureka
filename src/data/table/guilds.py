from data.table.channels import ChannelData
from data.table.definition import TableDefinition, ColumnType, ColumnFlag
from typing import List

from data.table.schedule import ScheduleType

class GuildData:
    guild_id: int
    schedule_channel: int
    schedule_post: int
    _channels: List[ChannelData]
    
    def __init__(self, guild_id: int, schedule_channel: int, schedule_post: int):
        self.guild_id = guild_id
        self.schedule_channel = schedule_channel
        self.schedule_post = schedule_post
        self._channels = []
    
    def get_channel(self, channel_id: int = 0, type: ScheduleType = '') -> ChannelData:
        if channel_id:
            for ch in self._channels:
                if ch.channel_id == channel_id:
                    return ch
        if type:
            for ch in self._channels:
                if ch.guild_id == self.guild_id and ch.type == type:
                    return ch
        ch = ChannelData(self.guild_id, '', channel_id)
        self._channels.append(ch)
        return ch

    def get_pl_channel(self, type: ScheduleType) -> ChannelData:
        for ch in self._channels:
            if ch.guild_id == self.guild_id and ch.type == type and ch.is_pl_channel:
                return ch
        return None
    
    def remove_channel(self, channel_id: int = 0, type: ScheduleType = ''):
        self._channels.remove(self.get_channel(channel_id, type))
        
    def add_channel(self, channel_id: int, type: ScheduleType, is_pl_channel: bool = False):
        self._channels.append(ChannelData(self.guild_id, type, channel_id, is_pl_channel))
        
    
class GuildTable(TableDefinition):
    def init_definitions(self):
        self.define_field('guild_id', ColumnType.BIGINT, 0, [ColumnFlag.UNIQUE, ColumnFlag.PRIMARY_KEY])
        self.define_field('schedule_channel', ColumnType.BIGINT)
        self.define_field('schedule_post', ColumnType.BIGINT)