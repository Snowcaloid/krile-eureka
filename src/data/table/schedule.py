from enum import Enum
import math
from data.table.definition import TableDefinition, ColumnType, ColumnFlag, ColumnDefinition
from typing import List
from datetime import datetime
from random import randint

class ScheduleType(Enum):
    BA_NORMAL = 'BA' 
    BA_RECLEAR = 'BARC'
    BA_SPECIAL = 'BASPEC'
    BA_ALL = 'BA_ALL'
    
def schedule_type_desc(type: ScheduleType) -> str:
    if type == ScheduleType.BA_NORMAL.value:
        return "Baldesion Arsenal Normal Run"
    elif type == ScheduleType.BA_RECLEAR.value:
        return "Baldesion Arsenal Reclear Run"
    elif type == ScheduleType.BA_SPECIAL.value:
        return "Baldesion Arsenal Special Run"
    elif type == ScheduleType.BA_ALL.value:
        return "All types of BA runs"
    
class ScheduleData:
    id: int
    owner: int
    type: ScheduleType
    timestamp: datetime
    description: str
    party_leaders: List[int]
    pass_main: int
    pass_supp: int
    post_id: int
    
    def __init__(self, owner: int, type: ScheduleType, timestamp: datetime, description: str) -> None:
        self.id = id
        self.owner = owner
        self.type = type
        self.timestamp = timestamp
        self.description = description
        self.party_leaders = [0,0,0,0,0,0,0]
        self.pass_main = 0
        self.pass_supp = 0
        self.post_id = 0
    
    def _gen_pass(self) -> int:
        result = 0
        for i in range(0, 4):
            result += randint(0, 9) * (math.pow(10, i))
        return result
    
    def generate_passcode(self, also_support: bool):
        if not self.pass_main:
            self.pass_main = self._gen_pass()
        if also_support:
            while not self.pass_supp or self.pass_supp == self.pass_main:
                self.pass_supp = self._gen_pass()
    
class ScheduleTable(TableDefinition):
    _columns: List[ColumnDefinition] = []
    def init_definitions(self):
        self.define_column('id', ColumnType.SERIAL, 0, [ColumnFlag.PRIMARY_KEY])
        self.define_column('schedule_post', ColumnType.BIGINT)
        self.define_column('type', ColumnType.VARCHAR, 15)
        self.define_column('timestamp', ColumnType.TIMESTAMP)
        self.define_column('description', ColumnType.TEXT)
        self.define_column('owner', ColumnType.BIGINT)
        self.define_column('pl1', ColumnType.BIGINT)
        self.define_column('pl2', ColumnType.BIGINT)
        self.define_column('pl3', ColumnType.BIGINT)
        self.define_column('pl4', ColumnType.BIGINT)
        self.define_column('pl5', ColumnType.BIGINT)
        self.define_column('pl6', ColumnType.BIGINT)
        self.define_column('pls', ColumnType.BIGINT)
        self.define_column('pass_main', ColumnType.INTEGER)
        self.define_column('pass_supp', ColumnType.INTEGER)
        self.define_column('post_id', ColumnType.BIGINT)