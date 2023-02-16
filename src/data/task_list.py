from datetime import datetime
import time as mod_time
from json import dumps, loads
from typing import List
import bot as task_list_bot
from data.table.database import pg_timestamp 
from data.table.tasks import TaskData, TaskExecutionType

class TaskList:
    _list: List[TaskData]
    
    def __init__(self) -> None:
        self._list = []
    
    def add_task(self, time: datetime, type: TaskExecutionType, data: object = None):
        taskdata = TaskData(time, type)
        taskdata.data = data
        self._list.append(taskdata)
        def sort(data: TaskData):
            dt = data.execution_time
            date_tuple = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
            return int(mod_time.mktime(datetime(*date_tuple).timetuple()))
        self._list.sort(key=sort)
        task_list_bot.snowcaloid.data.db.connect()
        try:
            id = task_list_bot.snowcaloid.data.db.query(f'insert into tasks (execution_time, task_type, data) values ({pg_timestamp(time)}, {type.value}, \'{dumps(data)}\') returning id')
            taskdata.id = id
        finally:
            task_list_bot.snowcaloid.data.db.disconnect()
            
    def empty(self) -> bool:
        return len(self._list) == 0
    
    def get_next(self) -> TaskData:
        if not self.empty():
            if self._list[0].execution_time <= datetime.utcnow():
                return self._list[0]
        return None
            
    def remove_task(self, id: int):
        for taskdata in self._list:
            if taskdata.id == id:
                self._list.remove(taskdata)
        task_list_bot.snowcaloid.data.db.connect()
        try:
            task_list_bot.snowcaloid.data.db.query(f'delete from tasks where id={id}')
        finally:
            task_list_bot.snowcaloid.data.db.disconnect()
            
    
    def load(self):
        task_list_bot.snowcaloid.data.db.connect()
        try:
            q = task_list_bot.snowcaloid.data.db.query('select id, execution_time, task_type, data from tasks order by execution_time')
            for record in q:
                taskdata = TaskData(record[1], record[2])
                taskdata.id = record[0]
                if record[3]:
                    taskdata.data = loads(record[3])
                self._list.append(taskdata)
        finally:
            task_list_bot.snowcaloid.data.db.disconnect()