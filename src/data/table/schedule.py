from enum import Enum
from data.table.definition import TableDefinition, ColumnType, ColumnFlag, ColumnDefinition
from typing import List
from datetime import datetime

class ScheduleType(Enum):
    BA_NORMAL = 'BA' 
    BA_RECLEAR = 'BARC'
    BA_SPECIAL = 'BASPEC'
    
def schedule_type_desc(type: ScheduleType) -> str:
    if type == ScheduleType.BA_NORMAL.value:
        return "Baldesion Arsenal normal run"
    elif type == ScheduleType.BA_RECLEAR.value:
        return "Baldesion Arsenal reclear run"
    elif type == ScheduleType.BA_SPECIAL.value:
        return "Baldesion Arsenal special run"
    
class ScheduleData:
    id: int
    user: int
    type: ScheduleType
    timestamp: datetime
    description: str
    
    def __init__(self, user: int, type: ScheduleType, timestamp: datetime, description: str) -> None:
        self.id = id
        self.user = user
        self.type = type
        self.timestamp = timestamp
        self.description = description
    
class ScheduleTable(TableDefinition):
    _columns: List[ColumnDefinition] = []
    def init_definitions(self):
        self.define_field('id', ColumnType.SERIAL, 0, [ColumnFlag.PRIMARY_KEY])
        self.define_field('user_id', ColumnType.BIGINT)
        self.define_field('schedule_post', ColumnType.BIGINT)
        self.define_field('type', ColumnType.VARCHAR, 15)
        self.define_field('timestamp', ColumnType.TIMESTAMP)
        self.define_field('description', ColumnType.TEXT)