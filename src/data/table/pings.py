from data.table.definition import TableDefinition, ColumnType, ColumnFlag
from enum import Enum
from typing import List

class PingType(Enum):
    NONE = 0
    MAIN_PASSCODE = 1
    SUPPORT_PASSCODE = 2
    PL_POST = 3

class PingsData:
    guild_id: int
    type: PingType
    tags: List[int]

    def __init__(self, guild_id: int, type: PingType, tags: List[int]):
        self.guild_id = guild_id
        self.type = type
        self.tags = tags

class PingsTable(TableDefinition):
    def init_definitions(self):
        self.define_column('id', ColumnType.SERIAL, 0, [ColumnFlag.UNIQUE])
        self.define_column('guild_id', ColumnType.BIGINT)
        self.define_column('type', ColumnType.VARCHAR, 15)
        self.define_column('tag', ColumnType.BIGINT)
