from enum import Enum
from data.table.definition import TableDefinition, ColumnType, ColumnFlag, ColumnDefinition
from typing import List
from datetime import datetime
from random import randint

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
    owner: int
    type: ScheduleType
    timestamp: datetime
    description: str
    party_leaders: List[int]
    pass_main: int
    pass_supp: int
    
    def __init__(self, owner: int, type: ScheduleType, timestamp: datetime, description: str) -> None:
        self.id = id
        self.owner = owner
        self.type = type
        self.timestamp = timestamp
        self.description = description
        self.party_leaders = [0,0,0,0,0,0,0]
        self.pass_main = 0
        self.pass_supp = 0
    
    def _gen_pass(self) -> int:
        result = 0
        for i in range(0, 3):
            result += randint(0, 9) * (10^i)
    
    def generate_passcode(self, also_support: bool):
        self.pass_main = self._gen_pass()
        if also_support:
            self.pass_supp = self._gen_pass()
    
class ScheduleTable(TableDefinition):
    _columns: List[ColumnDefinition] = []
    def init_definitions(self):
        self.define_field('id', ColumnType.SERIAL, 0, [ColumnFlag.PRIMARY_KEY])
        self.define_field('schedule_post', ColumnType.BIGINT)
        self.define_field('type', ColumnType.VARCHAR, 15)
        self.define_field('timestamp', ColumnType.TIMESTAMP)
        self.define_field('description', ColumnType.TEXT)
        self.define_field('owner', ColumnType.BIGINT)
        self.define_field('pl1', ColumnType.BIGINT)
        self.define_field('pl2', ColumnType.BIGINT)
        self.define_field('pl3', ColumnType.BIGINT)
        self.define_field('pl4', ColumnType.BIGINT)
        self.define_field('pl5', ColumnType.BIGINT)
        self.define_field('pl6', ColumnType.BIGINT)
        self.define_field('pls', ColumnType.BIGINT)
        self.define_field('pass_main', ColumnType.INTEGER)
        self.define_field('pass_supp', ColumnType.INTEGER)