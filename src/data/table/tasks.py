from datetime import datetime
from json import loads
from enum import Enum
from data.table.definition import TableDefinition, ColumnType

class TaskExecutionType(Enum):
    UPDATE_STATUS = 1
    SEND_PL_PASSCODES = 2
    REMOVE_OLD_RUNS = 3
    REMOVE_OLD_PL_POSTS = 4

class TaskData:
    id: int
    execution_time: datetime
    task_type: TaskExecutionType
    data: object
    
    def __init__(self, execution_time: datetime, task_type: TaskExecutionType):
        self.execution_time = execution_time
        self.task_type = task_type
        self.id = 0
        self.data = None
    
class TaskTable(TableDefinition):
    def init_definitions(self):
        self.define_column('id', ColumnType.SERIAL)
        self.define_column('execution_time', ColumnType.TIMESTAMP)
        self.define_column('task_type', ColumnType.INTEGER)
        self.define_column('data', ColumnType.TEXT)