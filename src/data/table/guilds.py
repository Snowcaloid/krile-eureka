from data.table.channels import ChannelData
from data.table.definition import TableDefinition, ColumnType, ColumnFlag
from typing import List

class GuildData:
    guild_id: int
    schedule_channel: int
    schedule_post: int
    channels: List[ChannelData]
    
    def __init__(self, guild_id: int, schedule_channel: int, schedule_post: int):
        self.guild_id = guild_id
        self.schedule_channel = schedule_channel
        self.schedule_post = schedule_post
        self.channels = []
    
class GuildTable(TableDefinition):
    def init_definitions(self):
        self.define_field('guild_id', ColumnType.BIGINT, 0, [ColumnFlag.UNIQUE, ColumnFlag.PRIMARY_KEY])
        self.define_field('schedule_channel', ColumnType.BIGINT)
        self.define_field('schedule_post', ColumnType.BIGINT)